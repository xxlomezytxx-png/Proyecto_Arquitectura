import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.application.pricing_use_cases import PricingService
from app.domain.pricing import BookCondition, PricingDecision
from app.infrastructure.database import get_db

router = APIRouter()
_use_mock = os.getenv("USE_MOCK_EBAY", "false").lower() == "true"
pricing_service = PricingService(use_mock=_use_mock)


class CalculatePriceRequest(BaseModel):
    book_id: str
    book_title: str
    condition: BookCondition
    author: Optional[str] = None


class PricingDecisionResponse(BaseModel):
    id: int
    book_id: str
    title: Optional[str]
    condition: str
    base_price: float
    condition_factor: float
    suggested_price: float
    references_used: int
    source: str
    is_fallback: bool
    explanation: str
    created_at: str


class PriceOverrideRequest(BaseModel):
    suggested_price: float
    reason: str = "manual override"


class APIStatusResponse(BaseModel):
    source: str
    available: bool
    last_check: str
    error_message: Optional[str]


@router.get("/", response_model=List[PricingDecisionResponse])
def list_pricing_decisions(limit: int = 100, db: Session = Depends(get_db)):
    """List all recent pricing decisions"""
    decisions = pricing_service.list_all_decisions(db, limit)
    return [
        PricingDecisionResponse(
            id=d.id,
            book_id=d.book_id,
            title=d.book_title,
            condition=d.condition.value,
            base_price=d.base_price,
            condition_factor=d.condition_factor,
            suggested_price=d.suggested_price,
            references_used=d.references_used,
            source=d.source,
            is_fallback=d.source == "fallback",
            explanation=d.explanation,
            created_at=d.created_at.isoformat()
        )
        for d in decisions
    ]


@router.post("/calculate", response_model=PricingDecisionResponse)
async def calculate_price(
    request: CalculatePriceRequest,
    db: Session = Depends(get_db)
):
    """Calculate suggested price for a book"""
    try:
        decision = await pricing_service.calculate_price(
            db=db,
            book_id=request.book_id,
            book_title=request.book_title,
            condition=request.condition,
            author=request.author
        )

        return PricingDecisionResponse(
            id=decision.id,
            book_id=decision.book_id,
            title=decision.book_title,
            condition=decision.condition.value,
            base_price=decision.base_price,
            condition_factor=decision.condition_factor,
            suggested_price=decision.suggested_price,
            references_used=decision.references_used,
            source=decision.source,
            is_fallback=decision.source == "fallback",
            explanation=decision.explanation,
            created_at=decision.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating price: {str(e)}")


@router.get("/explanation/{decision_id}")
def get_decision_explanation(decision_id: int, db: Session = Depends(get_db)):
    """Get explanation for a specific pricing decision"""
    explanation = pricing_service.get_decision_explanation(db, decision_id)
    if not explanation:
        raise HTTPException(status_code=404, detail="Decision not found")

    return {"decision_id": decision_id, "explanation": explanation}


@router.get("/external-apis/status", response_model=APIStatusResponse)
def get_external_api_status():
    """Get status of external APIs"""
    status = pricing_service.get_external_api_status()
    return APIStatusResponse(**status)


@router.get("/{book_id}", response_model=PricingDecisionResponse)
def get_latest_price(book_id: str, db: Session = Depends(get_db)):
    """Get the latest pricing decision for a book"""
    decision = pricing_service.get_latest_price(db, book_id)
    if not decision:
        raise HTTPException(status_code=404, detail="No pricing decision found for this book")

    return PricingDecisionResponse(
        id=decision.id,
        book_id=decision.book_id,
        title=decision.book_title,
        condition=decision.condition.value,
        base_price=decision.base_price,
        condition_factor=decision.condition_factor,
        suggested_price=decision.suggested_price,
        references_used=decision.references_used,
        source=decision.source,
        is_fallback=decision.source == "fallback",
        explanation=decision.explanation,
        created_at=decision.created_at.isoformat()
    )


@router.post("/{book_id}/override", response_model=PricingDecisionResponse)
def override_price(
    book_id: str,
    body: PriceOverrideRequest,
    db: Session = Depends(get_db),
):
    """Persist a manual price override as a new pricing decision."""
    from datetime import datetime, timezone
    from app.infrastructure.database import PricingDecisionModel, BookConditionDB

    decision_model = PricingDecisionModel(
        book_id=book_id,
        book_title=None,
        condition=BookConditionDB.BUENO,
        base_price=body.suggested_price,
        condition_factor=1.0,
        suggested_price=body.suggested_price,
        references_used=0,
        source="manual",
        explanation=body.reason,
    )
    db.add(decision_model)
    try:
        db.commit()
        db.refresh(decision_model)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving override: {exc}")

    return PricingDecisionResponse(
        id=decision_model.id,
        book_id=decision_model.book_id,
        title=decision_model.book_title,
        condition=decision_model.condition.value,
        base_price=decision_model.base_price,
        condition_factor=decision_model.condition_factor,
        suggested_price=decision_model.suggested_price,
        references_used=decision_model.references_used,
        source=decision_model.source,
        is_fallback=False,
        explanation=decision_model.explanation,
        created_at=decision_model.created_at.isoformat(),
    )


@router.get("/{book_id}/history", response_model=List[PricingDecisionResponse])
def get_price_history(book_id: str, db: Session = Depends(get_db)):
    """Get pricing history for a book"""
    decisions = pricing_service.get_price_history(db, book_id)

    return [
        PricingDecisionResponse(
            id=d.id,
            book_id=d.book_id,
            title=d.book_title,
            condition=d.condition.value,
            base_price=d.base_price,
            condition_factor=d.condition_factor,
            suggested_price=d.suggested_price,
            references_used=d.references_used,
            source=d.source,
            is_fallback=d.source == "fallback",
            explanation=d.explanation,
            created_at=d.created_at.isoformat()
        )
        for d in decisions
    ]
