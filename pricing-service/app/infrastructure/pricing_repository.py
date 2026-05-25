from typing import List, Optional
from sqlalchemy.orm import Session

from app.domain.pricing import PricingDecision, PricingReference, BookCondition
from app.infrastructure.database import PricingDecisionModel, PricingReferenceModel, BookConditionDB


def _reference_to_domain(model: PricingReferenceModel) -> PricingReference:
    return PricingReference(
        id=model.id,
        book_id=model.book_id,
        source=model.source,
        price=model.price,
        currency=model.currency,
        observed_at=model.observed_at,
        metadata=model.extra_data or {}
    )


def _decision_to_domain(model: PricingDecisionModel) -> PricingDecision:
    return PricingDecision(
        id=model.id,
        book_id=model.book_id,
        book_title=model.book_title,
        condition=BookCondition(model.condition.value),
        base_price=model.base_price,
        condition_factor=model.condition_factor,
        suggested_price=model.suggested_price,
        references_used=model.references_used,
        source=model.source,
        explanation=model.explanation,
        created_at=model.created_at,
        references=[_reference_to_domain(ref) for ref in model.references] if model.references else []
    )


def save_pricing_decision(db: Session, decision: PricingDecision) -> PricingDecision:
    # Save references first
    reference_models = []
    for ref in decision.references or []:
        ref_model = PricingReferenceModel(
            book_id=ref.book_id,
            source=ref.source,
            price=ref.price,
            currency=ref.currency,
            observed_at=ref.observed_at,
            extra_data=ref.metadata
        )
        db.add(ref_model)
        reference_models.append(ref_model)

    # Save decision
    decision_model = PricingDecisionModel(
        book_id=decision.book_id,
        book_title=decision.book_title,
        condition=decision.condition.value,
        base_price=decision.base_price,
        condition_factor=decision.condition_factor,
        suggested_price=decision.suggested_price,
        references_used=decision.references_used,
        source=decision.source,
        explanation=decision.explanation
    )
    db.add(decision_model)
    try:
        db.commit()
        db.refresh(decision_model)
    except Exception:
        db.rollback()
        raise
    return _decision_to_domain(decision_model)


def get_latest_pricing_decision(db: Session, book_id: str) -> Optional[PricingDecision]:
    model = db.query(PricingDecisionModel).filter(
        PricingDecisionModel.book_id == book_id
    ).order_by(PricingDecisionModel.created_at.desc()).first()
    return _decision_to_domain(model) if model else None


def get_pricing_history(db: Session, book_id: str) -> List[PricingDecision]:
    models = db.query(PricingDecisionModel).filter(
        PricingDecisionModel.book_id == book_id
    ).order_by(PricingDecisionModel.created_at.desc()).all()
    return [_decision_to_domain(model) for model in models]


def get_pricing_decision_by_id(db: Session, decision_id: int) -> Optional[PricingDecision]:
    model = db.query(PricingDecisionModel).filter(
        PricingDecisionModel.id == decision_id
    ).first()
    return _decision_to_domain(model) if model else None


def get_all_pricing_decisions(db: Session, limit: int = 100) -> List[PricingDecision]:
    models = db.query(PricingDecisionModel).order_by(
        PricingDecisionModel.created_at.desc()
    ).limit(limit).all()
    return [_decision_to_domain(m) for m in models]