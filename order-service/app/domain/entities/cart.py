from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class CartStatus(str, Enum):
    OPEN = "open"
    CHECKED_OUT = "checked_out"


@dataclass(frozen=True)
class CartItem:
    id: Optional[int]
    cart_id: int
    book_id: str
    book_title: str
    quantity: int
    unit_price: float


@dataclass(frozen=True)
class Cart:
    id: Optional[int]
    customer_id: str
    status: CartStatus
    items: List[CartItem] = field(default_factory=list)
