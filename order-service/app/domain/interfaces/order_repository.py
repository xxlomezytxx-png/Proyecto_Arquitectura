from __future__ import annotations

from typing import Optional, Protocol

from app.domain.entities.order import Order


class OrderRepository(Protocol):
    """Persistence contract for Order aggregates. Implementations live in
    infrastructure layer. Domain code depends only on this Protocol."""

    def create(self, order: Order) -> Order: ...

    def get_by_id(self, order_id: int) -> Optional[Order]: ...

    def list_by_customer(
        self, customer_id: str, limit: int = 50, offset: int = 0
    ) -> list[Order]: ...

    def list_all(self, limit: int = 50, offset: int = 0) -> list[Order]: ...

    def update(self, order: Order) -> Order: ...
