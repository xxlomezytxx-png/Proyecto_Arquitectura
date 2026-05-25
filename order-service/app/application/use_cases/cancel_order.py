from __future__ import annotations

from typing import Optional

from app.application.errors import OrderNotFoundError
from app.domain.entities.order import Order, OrderStatus
from app.domain.interfaces.order_repository import OrderRepository


class CancelOrderUseCase:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def execute(self, order_id: int, reason: Optional[str] = None) -> Order:
        order = self._repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        cancelled = order.transition_to(OrderStatus.CANCELLED, reason=reason)
        return self._repository.update(cancelled)
