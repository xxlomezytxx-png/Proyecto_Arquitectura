from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class OrderItemInput:
    book_id: str
    quantity: int
    unit_price_override: Optional[float] = None


@dataclass(frozen=True)
class CreateOrderInput:
    customer_id: str
    items: tuple[OrderItemInput, ...]
