import logging

from fastapi import FastAPI
from sqlalchemy import text

from app.infrastructure.database.connection import Base, engine, SessionLocal

logger = logging.getLogger(__name__)
from app.infrastructure.database.models import AssistantInteractionModel  # noqa: F401
from app.routers.chat_router import router as chat_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Assistant Service", version="1.0.0")

app.include_router(chat_router)


@app.get("/health")
def health() -> dict:
    db_status = "disconnected"
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        logger.warning("Health check DB probe failed: %s", exc)
    finally:
        db.close()
    return {"status": "ok", "service": "ai-assistant-service", "version": "1.0.0", "db": db_status}
