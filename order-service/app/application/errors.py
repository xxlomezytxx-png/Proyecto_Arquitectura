from __future__ import annotations

from dataclasses import dataclass


class OrderNotFoundError(LookupError):
    def __init__(self, order_id: int) -> None:
        super().__init__(f"order {order_id} not found")
        self.order_id = order_id


@dataclass(frozen=True)
class InsufficientStockLine:
    book_id: str
    requested: int
    available: int


class InsufficientStockError(RuntimeError):
    def __init__(self, shortages: tuple[InsufficientStockLine, ...]) -> None:
        details = ", ".join(
            f"{s.book_id} (need {s.requested}, have {s.available})" for s in shortages
        )
        super().__init__(f"insufficient stock: {details}")
        self.shortages = shortages
