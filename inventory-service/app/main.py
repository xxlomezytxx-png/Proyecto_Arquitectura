import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.infrastructure.database import Base, engine, SessionLocal

logger = logging.getLogger(__name__)
from app.routers import batch_router, inventory_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BookFlow — Inventory Service",
    description="Gestión de inventario y carga masiva de archivos",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inventory_router.router, prefix="/inventory", tags=["inventory"])
app.include_router(batch_router.router, prefix="/batches", tags=["batches"])


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
    return {"status": "ok", "service": "inventory-service", "version": "1.0.0", "db": db_status}
