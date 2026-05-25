import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.domain.user import User, UserRole
from app.infrastructure import user_repository
from app.infrastructure.database import RevokedTokenModel

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def create_token(data: dict, expires_delta: Optional[timedelta], token_type: str = "access") -> str:
    to_encode = data.copy()
    if token_type == "refresh":
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES))
    else:
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4()), "type": token_type})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return create_token(data, expires_delta, "access")


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return create_token(data, expires_delta, "refresh")


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        logger.debug("Token decode failed: %s", exc)
        return None


def is_token_revoked(db: Session, jti: str) -> bool:
    if not jti:
        return False
    return db.query(RevokedTokenModel).filter(RevokedTokenModel.jti == jti).first() is not None


def revoke_token(db: Session, jti: str) -> None:
    if not is_token_revoked(db, jti):
        try:
            db.add(RevokedTokenModel(jti=jti))
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.error("Failed to revoke token jti=%s: %s", jti, exc)
            raise


def register_user(db: Session, username: str, email: str, password: str, role: str = "user") -> User:
    if user_repository.get_user_by_username(db, username):
        raise ValueError("El usuario ya existe")
    if user_repository.get_user_by_email(db, email):
        raise ValueError("El email ya está registrado")
    user = User(
        id=None,
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=UserRole(role),
        is_active=True,
        created_at=None,
    )
    return user_repository.create_user(db, user)


def login_user(db: Session, username: str, password: str) -> tuple[Optional[str], Optional[str]]:
    user = user_repository.get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        logger.warning("AUTH_FAILURE username=%s", username)
        return None, None
    logger.info("AUTH_SUCCESS username=%s role=%s", username, user.role.value)
    data = {"sub": user.username, "role": user.role.value, "user_id": user.id}
    return create_access_token(data), create_refresh_token(data)
