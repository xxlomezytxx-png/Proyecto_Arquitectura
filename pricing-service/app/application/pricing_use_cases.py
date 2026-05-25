from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import logging
import requests

from sqlalchemy.orm import Session

from app.config import settings
from app.domain.pricing import PricingDecision, PricingReference, BookCondition
from app.infrastructure.pricing_repository import (
    save_pricing_decision,
    get_latest_pricing_decision,
    get_pricing_history,
    get_pricing_decision_by_id,
    get_all_pricing_decisions,
)
from app.infrastructure.adapters.ebay_adapter import EbayAdapter, MockEbayAdapter

logger = logging.getLogger(__name__)


def update_catalog_price(book_id: str, price: float):
    try:
        requests.patch(
            f"{settings.CATALOG_SERVICE_URL}/products/{book_id}/price",
            json={"price": price},
            timeout=10,
        )
    except Exception as exc:
        logger.warning("No se pudo actualizar precio en catálogo: %s", exc)


class PricingService:
    def __init__(self, use_mock: bool = False):
        self.adapter = MockEbayAdapter() if use_mock else EbayAdapter()

    async def calculate_price(
        self,
        db: Session,
        book_id: str,
        book_title: str,
        condition: BookCondition,
        author: str = None,
    ) -> PricingDecision:

        try:
            references = await self.adapter.get_book_prices(book_title, author)
            references_used = len(references)

            if references_used > 0:
                source = "external"
                base_price = self._calculate_base_price(references)
            else:
                source = "fallback"
                base_price = self._fallback_base_price(book_title)

        except Exception as e:
            logger.warning("External API failed: %s. Using fallback.", e)
            references = []
            references_used = 0
            source = "fallback"
            base_price = self._fallback_base_price(book_title)

        condition_factor = settings.CONDITION_FACTORS.get(condition.value, 1.0)

        suggested_price = base_price * condition_factor

        if suggested_price < 1000:
            suggested_price = suggested_price * settings.USD_TO_COP

        if suggested_price < settings.MIN_PRICE_THRESHOLD:
            suggested_price = settings.MIN_PRICE_THRESHOLD

        suggested_price = round(suggested_price, 0)

        explanation = self._build_explanation(
            base_price,
            condition_factor,
            suggested_price,
            references_used,
            source,
            condition,
        )

        decision = PricingDecision(
            id=None,
            book_id=book_id,
            book_title=book_title,
            condition=condition,
            base_price=base_price,
            condition_factor=condition_factor,
            suggested_price=suggested_price,
            references_used=references_used,
            source=source,
            explanation=explanation,
            created_at=datetime.now(timezone.utc),
            references=references,
        )

        saved_decision = save_pricing_decision(db, decision)

        update_catalog_price(str(book_id), float(suggested_price))

        return saved_decision

    def _calculate_base_price(self, references: List[PricingReference]) -> float:
        prices = [ref.price for ref in references]
        sorted_prices = sorted(prices)
        n = len(sorted_prices)

        if n % 2 == 0:
            base_price = (sorted_prices[n // 2 - 1] + sorted_prices[n // 2]) / 2
        else:
            base_price = sorted_prices[n // 2]

        return round(base_price, 2)

    def _fallback_base_price(self, book_title: str) -> float:
        title_length = len(book_title or "")
        base_usd = 8.0 + (title_length * 0.1)
        return min(base_usd, 25.0)

    def _build_explanation(
        self,
        base_price: float,
        condition_factor: float,
        suggested_price: float,
        references_used: int,
        source: str,
        condition: BookCondition,
    ) -> str:
        explanation = f"Precio base calculado: {base_price:.2f}. "

        if source == "external":
            explanation += f"Basado en {references_used} referencias externas. "
        else:
            explanation += "Usando lógica interna de fallback. "

        explanation += f"Factor de condición '{condition.value}': {condition_factor}. "
        explanation += f"Precio sugerido final en COP: {suggested_price:,.0f}."

        return explanation

    def get_latest_price(self, db: Session, book_id: str) -> Optional[PricingDecision]:
        return get_latest_pricing_decision(db, book_id)

    def get_price_history(self, db: Session, book_id: str) -> List[PricingDecision]:
        return get_pricing_history(db, book_id)

    def get_decision_explanation(self, db: Session, decision_id: int) -> Optional[str]:
        decision = get_pricing_decision_by_id(db, decision_id)
        return decision.explanation if decision else None

    def list_all_decisions(self, db: Session, limit: int = 100) -> List[PricingDecision]:
        return get_all_pricing_decisions(db, limit)

    def get_external_api_status(self) -> Dict[str, Any]:
        return self.adapter.get_status()