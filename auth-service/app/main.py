import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.infrastructure.database import Base, SessionLocal, engine
from app.routers import auth_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)


def _seed_admin() -> None:
    """Create default admin user on startup if it doesn't exist."""
    from app.application.auth_use_cases import register_user  # local import avoids circular dep

    username = os.getenv("ADMIN_USERNAME", "admin")
    email = os.getenv("ADMIN_EMAIL", "admin@bookflow.com")
    password = os.getenv("ADMIN_PASSWORD", "admin123!")

    db = SessionLocal()
    try:
        register_user(db, username, email, password, role="admin")
        logger.info("SEED admin user '%s' created", username)
    except ValueError:
        logger.debug("SEED admin user '%s' already exists — skip", username)
    except Exception as exc:
        logger.warning("SEED admin user creation failed: %s", exc)
    finally:
        db.close()


_seed_admin()

app = FastAPI(
    title="BookFlow — Auth Service",
    description="Autenticación JWT para la plataforma BookFlow",
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.BFF_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="", tags=["auth"])


@app.get("/health")
def health():
    db_status = "connected"
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"
    finally:
        db.close()
    return {
        "status": "ok",
        "service": "auth-service",
        "db": db_status,
        "version": settings.APP_VERSION,
    }
