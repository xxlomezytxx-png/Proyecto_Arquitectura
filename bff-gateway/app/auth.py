"""JWT authentication dependency for the BFF gateway.

Shares the same secret/algorithm already used by AdminAuthMiddleware in main.py.
Import `require_auth` and add it as a FastAPI dependency on routes that need
a valid JWT — without duplicating the verification logic.
"""
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

_JWT_SECRET = os.getenv("JWT_SECRET_KEY")
_JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

_bearer = HTTPBearer(auto_error=False)


def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    """FastAPI dependency — raises 401 if the JWT is missing or invalid.

    Usage::

        @router.post("/api/orders", dependencies=[Depends(require_auth)])
        async def create_order(...): ...

    Returns the decoded token payload so individual routes can inspect
    ``role``, ``sub``, etc. when needed.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not _JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET_KEY not configured on the server",
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            _JWT_SECRET,
            algorithms=[_JWT_ALGORITHM],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
