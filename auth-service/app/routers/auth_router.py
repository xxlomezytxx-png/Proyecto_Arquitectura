from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.application.auth_use_cases import (
    create_access_token, decode_token, is_token_revoked,
    login_user, register_user, revoke_token,
)
from app.domain.user import UserRole
from app.infrastructure.database import get_db

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_Token = Annotated[str, Depends(oauth2_scheme)]
_DB = Annotated[Session, Depends(get_db)]


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", status_code=201, responses={400: {"description": "Username or email already taken"}})
def register(req: RegisterRequest, db: _DB):
    try:
        user = register_user(db, req.username, req.email, req.password, req.role.value)
        return {"message": "Usuario registrado", "username": user.username, "role": user.role.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse, responses={401: {"description": "Invalid credentials"}})
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: _DB):
    access_token, refresh_token = login_user(db, form.username, form.password)
    if not access_token:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    payload = decode_token(access_token)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        role=payload["role"],
    )


@router.post("/refresh", response_model=TokenResponse, responses={401: {"description": "Invalid or revoked refresh token"}})
def refresh(req: RefreshRequest, db: _DB):
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")

    if is_token_revoked(db, payload.get("jti")):
        raise HTTPException(status_code=401, detail="Refresh token revocado")

    data = {"sub": payload.get("sub"), "role": payload.get("role"), "user_id": payload.get("user_id")}
    new_access_token = create_access_token(data)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=req.refresh_token,
        token_type="bearer",
        role=payload.get("role"),
    )


@router.post("/logout")
def logout(token: _Token, db: _DB):
    payload = decode_token(token)
    if payload and payload.get("jti"):
        revoke_token(db, payload.get("jti"))
    return {"message": "Sesión cerrada correctamente"}


@router.get("/me", responses={401: {"description": "Invalid or revoked token"}})
def get_current_user(token: _Token, db: _DB):
    payload = decode_token(token)
    if not payload or payload.get("type") == "refresh":
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    if is_token_revoked(db, payload.get("jti")):
        raise HTTPException(status_code=401, detail="Token revocado")
    return {
        "username": payload.get("sub"),
        "role": payload.get("role"),
        "user_id": payload.get("user_id"),
    }


@router.get("/verify", responses={401: {"description": "Invalid or revoked token"}})
def verify(token: _Token, db: _DB):
    payload = decode_token(token)
    if not payload or payload.get("type") == "refresh":
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    if is_token_revoked(db, payload.get("jti")):
        raise HTTPException(status_code=401, detail="Token revocado")

    return {
        "username": payload.get("sub"),
        "role": payload.get("role"),
        "user_id": payload.get("user_id"),
    }
