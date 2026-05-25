import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.infrastructure.database import Base, engine, SessionLocal

logger = logging.getLogger(__name__)
from app.infrastructure.catalog_repository import seed_categories, seed_products
from app.routers import catalog_router, category_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_categories(db)
        seed_products(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="TechFlow — Catalog Service",
    description="Catálogo comercial de tecnología, PCs, componentes y servicios de ensamblaje.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(category_router.router, prefix="/categories", tags=["categories"])
app.include_router(catalog_router.router, prefix="/products", tags=["products"])
app.include_router(catalog_router.router, prefix="/books", tags=["books"])


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
    return {"status": "ok", "service": "catalog-service", "version": "1.0.0", "db": db_status}
