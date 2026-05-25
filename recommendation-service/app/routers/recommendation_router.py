from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.application.use_cases.recommend_use_case import RecommendUseCase
from app.infrastructure.clients.catalog_client import CatalogClient
from app.infrastructure.clients.inventory_client import InventoryClient

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

class RecommendedBookResponse(BaseModel):
    book_id: str
    title: str
    author: str
    category: str
    score: float
    reason: str

@router.get("/{book_id}", response_model=list[RecommendedBookResponse])
async def get_recommendations(book_id: str) -> list[RecommendedBookResponse]:
    use_case = RecommendUseCase(
        catalog=CatalogClient(),
        inventory=InventoryClient(),
    )
    recommendations = await use_case.execute(book_id)
    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail=f"No recommendations found for book {book_id}",
        )
    return [
        RecommendedBookResponse(
            book_id=r.book_id,
            title=r.title,
            author=r.author,
            category=r.category,
            score=r.score,
            reason=r.reason,
        )
        for r in recommendations
    ]