from __future__ import annotations

from typing import Optional

import pytest

from app.application.dtos import CreateOrderInput, OrderItemInput
from app.application.use_cases.cancel_order import CancelOrderUseCase
from app.application.use_cases.confirm_order import (ConfirmOrderUseCase,
                                                     InsufficientStockError,
                                                     OrderNotFoundError)
from app.application.use_cases.create_order import (BookNotFoundError,
                                                    CreateOrderUseCase,
                                                    MissingPriceError)
from app.application.use_cases.fulfill_order import FulfillOrderUseCase
from app.domain.entities.order import (IllegalStateTransitionError, Order,
                                       OrderItem, OrderStatus)
from app.domain.interfaces.catalog_client import CatalogBook
from app.domain.interfaces.inventory_client import StockLevel
from app.domain.interfaces.pricing_client import PriceQuote


pytestmark = pytest.mark.unit


# ─── Fakes ────────────────────────────────────────────────────────────


class FakeOrderRepo:
    def __init__(self) -> None:
        self._store: dict[int, Order] = {}
        self._next_id = 1

    def create(self, order: Order) -> Order:
        new_id = self._next_id
        self._next_id += 1
        # Copy with id assigned (frozen dataclass — use replace)
        from dataclasses import replace

        saved = replace(order, id=new_id)
        self._store[new_id] = saved
        return saved

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return self._store.get(order_id)

    def list_by_customer(self, customer_id: str, limit: int = 50, offset: int = 0) -> list[Order]:
        return [o for o in self._store.values() if o.customer_id == customer_id]

    def update(self, order: Order) -> Order:
        if order.id is None or order.id not in self._store:
            raise LookupError(f"order {order.id} not found")
        self._store[order.id] = order
        return order


class FakeCatalogClient:
    def __init__(self, books: dict[str, CatalogBook]) -> None:
        self._books = books

    async def get_book(self, book_id: str) -> Optional[CatalogBook]:
        return self._books.get(book_id)


class FakePricingClient:
    def __init__(self, quotes: dict[str, PriceQuote]) -> None:
        self._quotes = quotes

    async def get_latest_price(self, book_id: str) -> Optional[PriceQuote]:
        return self._quotes.get(book_id)


class FakeInventoryClient:
    def __init__(self, stock: dict[str, int]) -> None:
        self._stock = stock
        self.calls: list[str] = []
        self.reservations: list[tuple[str, int]] = []

    async def get_stock(self, book_id: str) -> StockLevel:
        self.calls.append(book_id)
        return StockLevel(book_id=book_id, available=self._stock.get(book_id, 0))

    async def reserve_stock(self, book_id: str, quantity: int) -> None:
        self.reservations.append((book_id, quantity))


# ─── CreateOrderUseCase ───────────────────────────────────────────────


class TestCreateOrderUseCase:
    @pytest.mark.asyncio
    async def test_creates_pending_order_with_pricing_snapshot(self) -> None:
        repo = FakeOrderRepo()
        catalog = FakeCatalogClient({"b1": CatalogBook(book_id="b1", title="Clean Code")})
        pricing = FakePricingClient({"b1": PriceQuote(book_id="b1", suggested_price=12.5, source="external")})
        use_case = CreateOrderUseCase(repo, catalog, pricing)

        order = await use_case.execute(
            CreateOrderInput(
                customer_id="cust-1",
                items=(OrderItemInput(book_id="b1", quantity=2),),
            )
        )

        assert order.id == 1
        assert order.status is OrderStatus.PENDING
        assert order.items[0].unit_price == 12.5
        assert order.items[0].book_title == "Clean Code"
        assert order.total_amount == 25.0

    @pytest.mark.asyncio
    async def test_unknown_book_raises_book_not_found(self) -> None:
        repo = FakeOrderRepo()
        catalog = FakeCatalogClient(books={})
        pricing = FakePricingClient(quotes={})
        use_case = CreateOrderUseCase(repo, catalog, pricing)

        with pytest.raises(BookNotFoundError):
            await use_case.execute(
                CreateOrderInput(
                    customer_id="cust-1",
                    items=(OrderItemInput(book_id="missing", quantity=1),),
                )
            )

    @pytest.mark.asyncio
    async def test_no_price_quote_raises_missing_price(self) -> None:
        repo = FakeOrderRepo()
        catalog = FakeCatalogClient({"b1": CatalogBook(book_id="b1", title="t1")})
        pricing = FakePricingClient(quotes={})  # no quote for b1
        use_case = CreateOrderUseCase(repo, catalog, pricing)

        with pytest.raises(MissingPriceError):
            await use_case.execute(
                CreateOrderInput(
                    customer_id="cust-1",
                    items=(OrderItemInput(book_id="b1", quantity=1),),
                )
            )

    @pytest.mark.asyncio
    async def test_unit_price_override_skips_pricing_lookup(self) -> None:
        repo = FakeOrderRepo()
        catalog = FakeCatalogClient({"b1": CatalogBook(book_id="b1", title="t1")})
        pricing = FakePricingClient(quotes={})  # would fail without override
        use_case = CreateOrderUseCase(repo, catalog, pricing)

        order = await use_case.execute(
            CreateOrderInput(
                customer_id="cust-1",
                items=(OrderItemInput(book_id="b1", quantity=1, unit_price_override=99.0),),
            )
        )
        assert order.items[0].unit_price == 99.0


# ─── ConfirmOrderUseCase ──────────────────────────────────────────────


class TestConfirmOrderUseCase:
    @pytest.mark.asyncio
    async def test_confirm_calls_inventory_for_each_item(self) -> None:
        repo = FakeOrderRepo()
        seeded = repo.create(
            Order(
                customer_id="c1",
                items=(
                    OrderItem("b1", "t1", 2, 10.0),
                    OrderItem("b2", "t2", 1, 5.0),
                ),
            )
        )
        inventory = FakeInventoryClient({"b1": 10, "b2": 5})
        use_case = ConfirmOrderUseCase(repo, inventory)

        confirmed = await use_case.execute(seeded.id)

        assert confirmed.status is OrderStatus.CONFIRMED
        assert sorted(inventory.calls) == ["b1", "b2"]

    @pytest.mark.asyncio
    async def test_insufficient_stock_keeps_order_pending(self) -> None:
        repo = FakeOrderRepo()
        seeded = repo.create(
            Order(
                customer_id="c1",
                items=(OrderItem("b1", "t1", 5, 10.0),),
            )
        )
        inventory = FakeInventoryClient({"b1": 2})
        use_case = ConfirmOrderUseCase(repo, inventory)

        with pytest.raises(InsufficientStockError) as excinfo:
            await use_case.execute(seeded.id)

        # Order must NOT have transitioned
        still_pending = repo.get_by_id(seeded.id)
        assert still_pending.status is OrderStatus.PENDING
        # Shortage details must be exact
        shortages = excinfo.value.shortages
        assert len(shortages) == 1
        assert shortages[0].book_id == "b1"
        assert shortages[0].requested == 5
        assert shortages[0].available == 2

    @pytest.mark.asyncio
    async def test_confirm_unknown_order_raises(self) -> None:
        repo = FakeOrderRepo()
        inventory = FakeInventoryClient(stock={})
        use_case = ConfirmOrderUseCase(repo, inventory)

        with pytest.raises(OrderNotFoundError):
            await use_case.execute(999)

    @pytest.mark.asyncio
    async def test_cannot_confirm_already_cancelled_order(self) -> None:
        repo = FakeOrderRepo()
        seeded = repo.create(Order(customer_id="c1", items=(OrderItem("b1", "t1", 1, 1.0),)))
        cancelled = seeded.transition_to(OrderStatus.CANCELLED, reason="test")
        repo.update(cancelled)

        inventory = FakeInventoryClient({"b1": 100})
        use_case = ConfirmOrderUseCase(repo, inventory)

        with pytest.raises(IllegalStateTransitionError):
            await use_case.execute(seeded.id)


# ─── Fulfill / Cancel ─────────────────────────────────────────────────


class TestFulfillOrderUseCase:
    def test_fulfill_only_after_confirmation(self) -> None:
        repo = FakeOrderRepo()
        seeded = repo.create(Order(customer_id="c1", items=(OrderItem("b1", "t1", 1, 1.0),)))
        use_case = FulfillOrderUseCase(repo)

        with pytest.raises(IllegalStateTransitionError):
            use_case.execute(seeded.id)

    def test_fulfill_confirmed_order(self) -> None:
        repo = FakeOrderRepo()
        seeded = repo.create(Order(customer_id="c1", items=(OrderItem("b1", "t1", 1, 1.0),)))
        repo.update(seeded.transition_to(OrderStatus.CONFIRMED))
        use_case = FulfillOrderUseCase(repo)

        fulfilled = use_case.execute(seeded.id)

        assert fulfilled.status is OrderStatus.FULFILLED
        assert fulfilled.fulfilled_at is not None


class TestCancelOrderUseCase:
    def test_cancel_pending_order_records_reason(self) -> None:
        repo = FakeOrderRepo()
        seeded = repo.create(Order(customer_id="c1", items=(OrderItem("b1", "t1", 1, 1.0),)))
        use_case = CancelOrderUseCase(repo)

        cancelled = use_case.execute(seeded.id, reason="duplicate order")

        assert cancelled.status is OrderStatus.CANCELLED
        assert cancelled.cancel_reason == "duplicate order"
