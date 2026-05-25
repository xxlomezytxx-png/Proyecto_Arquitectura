from fastapi import FastAPI
from app.routers.enrichment_router import router as enrichment_router
from app.routers.adapters_router import router as adapters_router

app = FastAPI(title="AI Enrichment Mock", version="1.0.0")
app.include_router(enrichment_router, prefix="/enrichment")
app.include_router(adapters_router, prefix="/adapters")
