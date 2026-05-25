from __future__ import annotations

from app.application.errors import OrderNotFoundError
from app.domain.entities.order import Order, OrderStatus
from app.domain.interfaces.order_repository import OrderRepository


class FulfillOrderUseCase:
    """Transition CONFIRMED -> FULFILLED. Marks an order as delivered.
    State machine raises if the order is not CONFIRMED."""

    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def execute(self, order_id: int) -> Order:
        order = self._repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        fulfilled = order.transition_to(OrderStatus.FULFILLED)
        return self._repository.update(fulfilled)
