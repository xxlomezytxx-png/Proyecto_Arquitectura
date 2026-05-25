from __future__ import annotations

import logging

from app.application.dtos import CreateOrderInput
from app.domain.entities.order import Order, OrderItem, OrderStatus
from app.domain.interfaces.catalog_client import CatalogClient
from app.domain.interfaces.order_repository import OrderRepository
from app.domain.interfaces.pricing_client import PricingClient

logger = logging.getLogger(__name__)


class BookNotFoundError(LookupError):
    def __init__(self, book_id: str) -> None:
        super().__init__(f"book {book_id} not found in catalog")
        self.book_id = book_id


class MissingPriceError(RuntimeError):
    def __init__(self, book_id: str) -> None:
        super().__init__(f"no price quote available for book {book_id}")
        self.book_id = book_id


class CreateOrderUseCase:
    """Validate every line item against catalog, snapshot pricing, persist
    a PENDING order. No stock check here — confirmation is a separate
    transition (see ConfirmOrderUseCase)."""

    def __init__(
        self,
        repository: OrderRepository,
        catalog_client: CatalogClient,
        pricing_client: PricingClient,
    ) -> None:
        self._repository = repository
        self._catalog_client = catalog_client
        self._pricing_client = pricing_client

    async def execute(self, payload: CreateOrderInput) -> Order:
        if not payload.items:
            raise ValueError("Order must contain at least one item")

        items: list[OrderItem] = []
        for line in payload.items:
            book = await self._catalog_client.get_book(line.book_id)
            if book is None:
                raise BookNotFoundError(line.book_id)

            unit_price = line.unit_price_override
            if unit_price is None:
                quote = await self._pricing_client.get_latest_price(line.book_id)
                if quote is None:
                    raise MissingPriceError(line.book_id)
                unit_price = quote.suggested_price

            isbn_raw = book.isbn or ""
            book_reference = isbn_raw.replace("-", "") or None
            items.append(
                OrderItem(
                    book_id=str(book.book_id),
                    book_title=book.title,
                    quantity=line.quantity,
                    unit_price=float(unit_price),
                    book_reference=book_reference,
                )
            )

        order = Order(
            customer_id=payload.customer_id,
            items=tuple(items),
            status=OrderStatus.PENDING,
        )
        return self._repository.create(order)
