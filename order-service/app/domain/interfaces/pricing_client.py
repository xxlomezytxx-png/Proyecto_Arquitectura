from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass(frozen=True)
class PriceQuote:
    book_id: str
    suggested_price: float
    source: str


class PricingClient(Protocol):
    """Port for fetching latest pricing decision. Optional dependency:
    callers must tolerate None when no decision exists yet."""

    async def get_latest_price(self, book_id: str) -> Optional[PriceQuote]: ...
