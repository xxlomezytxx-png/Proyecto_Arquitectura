import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.infrastructure.database import Base, engine, SessionLocal
from app.routers.pricing_router import router as pricing_router

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BookFlow — Pricing Service",
    description="Servicio de cálculo de precios sugeridos para libros",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pricing_router, prefix="/pricing", tags=["pricing"])


@app.get("/health")
def health():
    db_status = "disconnected"
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        logger.warning("Health check DB probe failed: %s", exc)
    finally:
        db.close()
    return {"status": "ok", "service": "pricing-service", "version": "1.0.0", "db": db_status}
