import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)

from app.routers.gateway_router import router

_JWT_SECRET = os.getenv("JWT_SECRET_KEY")
if not _JWT_SECRET:
    raise RuntimeError("JWT_SECRET_KEY environment variable is required")
_JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


class AdminAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api/admin"):
            return await call_next(request)

        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse({"detail": "No autenticado"}, status_code=401)

        token = auth.removeprefix("Bearer ").strip()
        try:
            payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
            if payload.get("role") != "admin":
                return JSONResponse({"detail": "Acceso denegado"}, status_code=403)
        except JWTError:
            return JSONResponse({"detail": "Token inválido"}, status_code=401)

        return await call_next(request)


app = FastAPI(
    title="BFF Gateway",
    description="Proxy central que enruta peticiones de los frontends hacia los microservicios.",
    version="2.0.0",
)

app.add_middleware(AdminAuthMiddleware)

_CORS_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def init_audit_db() -> None:
    try:
        from app.audit.connection import Base, engine
        from app.audit.models import AuditEntry  # noqa: F401
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        logger.warning("Audit DB init failed — will retry on next request: %s", exc)


app.include_router(router)
