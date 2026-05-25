from __future__ import annotations

import logging

from app.application.errors import (InsufficientStockError,
                                    InsufficientStockLine, OrderNotFoundError)
from app.domain.entities.order import (IllegalStateTransitionError, Order,
                                       OrderStatus)
from app.domain.interfaces.inventory_client import InventoryClient
from app.domain.interfaces.order_repository import OrderRepository

logger = logging.getLogger(__name__)


class ConfirmOrderUseCase:
    """Transition a PENDING order to CONFIRMED only when inventory-service
    reports enough stock for every line. No partial confirmations."""

    def __init__(
        self,
        repository: OrderRepository,
        inventory_client: InventoryClient,
    ) -> None:
        self._repository = repository
        self._inventory_client = inventory_client

    async def execute(self, order_id: int) -> Order:
        order = self._repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)

        if order.status is not OrderStatus.PENDING:
            raise IllegalStateTransitionError(
                f"Order {order_id} is {order.status.value}, can only confirm PENDING"
            )

        shortages: list[InsufficientStockLine] = []
        for item in order.items:
            lookup_key = item.book_reference or item.book_id
            level = await self._inventory_client.get_stock(lookup_key)
            if level.available < item.quantity:
                shortages.append(
                    InsufficientStockLine(
                        book_id=item.book_id,
                        requested=item.quantity,
                        available=level.available,
                    )
                )
        if shortages:
            raise InsufficientStockError(tuple(shortages))

        for item in order.items:
            lookup_key = item.book_reference or item.book_id
            await self._inventory_client.reserve_stock(lookup_key, item.quantity)

        confirmed = order.transition_to(OrderStatus.CONFIRMED)
        return self._repository.update(confirmed)
