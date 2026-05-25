from fastapi import FastAPI

from app.routers.recommendation_router import router as recommendation_router

app = FastAPI(title="Recommendation Service", version="1.0.0")

app.include_router(recommendation_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "recommendation-service", "version": "1.0.0", "db": "n/a"}
