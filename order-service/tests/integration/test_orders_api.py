from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from typing import Iterator, Optional

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


pytestmark = pytest.mark.integration


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """Spin up the FastAPI app against in-memory sqlite, with HTTP clients
    overridden by deterministic in-memory fakes. No external services."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    # Re-bind app's connection module to the test engine BEFORE create_all/import main.
    from app.infrastructure.database import connection as conn_module
    from app.infrastructure.database import models  # noqa: F401  registers tables

    conn_module.engine = engine
    conn_module.SessionLocal = TestingSession
    conn_module.Base.metadata.create_all(bind=engine)

    from app.domain.interfaces.catalog_client import CatalogBook
    from app.domain.interfaces.inventory_client import StockLevel
    from app.domain.interfaces.pricing_client import PriceQuote

    class FakeCatalog:
        async def get_book(self, book_id: str) -> Optional[CatalogBook]:
            if book_id in {"b1", "b2"}:
                return CatalogBook(book_id=book_id, title=f"Title {book_id}")
            return None

    class FakePricing:
        async def get_latest_price(self, book_id: str) -> Optional[PriceQuote]:
            return PriceQuote(book_id=book_id, suggested_price=10.0, source="external")

    class FakeInventory:
        def __init__(self) -> None:
            self.stock = {"b1": 100, "b2": 1}

        async def get_stock(self, book_id: str) -> StockLevel:
            return StockLevel(book_id=book_id, available=self.stock.get(book_id, 0))

        async def reserve_stock(self, book_id: str, quantity: int) -> None:
            pass

    inventory_fake = FakeInventory()

    from app import dependencies as deps
    from app.main import app

    def _get_session() -> Iterator[Session]:
        s = TestingSession()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[conn_module.get_db] = _get_session
    app.dependency_overrides[deps.get_catalog_client] = lambda: FakeCatalog()
    app.dependency_overrides[deps.get_pricing_client] = lambda: FakePricing()
    app.dependency_overrides[deps.get_inventory_client] = lambda: inventory_fake

    with TestClient(app) as c:
        c.inventory_fake = inventory_fake  # type: ignore[attr-defined]
        yield c

    app.dependency_overrides.clear()
    conn_module.Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_health_endpoint_responds_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "order-service"


def test_create_order_returns_201_with_pending_status(client: TestClient) -> None:
    response = client.post(
        "/orders",
        json={"customer_id": "cust-1", "items": [{"book_id": "b1", "quantity": 2}]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "PENDING"
    assert body["total_amount"] == 20.0
    assert body["items"][0]["book_title"] == "Title b1"


def test_create_order_unknown_book_returns_404(client: TestClient) -> None:
    response = client.post(
        "/orders",
        json={"customer_id": "cust-1", "items": [{"book_id": "missing", "quantity": 1}]},
    )
    assert response.status_code == 404


def test_create_then_confirm_flow(client: TestClient) -> None:
    create = client.post(
        "/orders",
        json={"customer_id": "cust-1", "items": [{"book_id": "b1", "quantity": 1}]},
    )
    order_id = create.json()["id"]

    confirm = client.post(f"/orders/{order_id}/confirm")
    assert confirm.status_code == 200
    assert confirm.json()["status"] == "CONFIRMED"


def test_confirm_with_insufficient_stock_returns_409(client: TestClient) -> None:
    create = client.post(
        "/orders",
        json={"customer_id": "cust-1", "items": [{"book_id": "b2", "quantity": 5}]},
    )
    order_id = create.json()["id"]

    confirm = client.post(f"/orders/{order_id}/confirm")
    assert confirm.status_code == 409
    body = confirm.json()
    assert body["detail"]["error"] == "insufficient_stock"
    assert body["detail"]["shortages"][0]["book_id"] == "b2"
    assert body["detail"]["shortages"][0]["available"] == 1

    # Verify order remained PENDING
    detail = client.get(f"/orders/{order_id}")
    assert detail.json()["status"] == "PENDING"


def test_double_confirm_returns_409(client: TestClient) -> None:
    create = client.post(
        "/orders",
        json={"customer_id": "cust-1", "items": [{"book_id": "b1", "quantity": 1}]},
    )
    order_id = create.json()["id"]
    client.post(f"/orders/{order_id}/confirm")

    second = client.post(f"/orders/{order_id}/confirm")
    assert second.status_code == 409


def test_full_lifecycle_create_confirm_fulfill(client: TestClient) -> None:
    create = client.post(
        "/orders",
        json={"customer_id": "cust-1", "items": [{"book_id": "b1", "quantity": 1}]},
    )
    order_id = create.json()["id"]
    client.post(f"/orders/{order_id}/confirm")
    fulfill = client.post(f"/orders/{order_id}/fulfill")
    assert fulfill.status_code == 200
    assert fulfill.json()["status"] == "FULFILLED"


def test_fulfill_pending_order_returns_409(client: TestClient) -> None:
    create = client.post(
        "/orders",
        json={"customer_id": "cust-1", "items": [{"book_id": "b1", "quantity": 1}]},
    )
    order_id = create.json()["id"]

    response = client.post(f"/orders/{order_id}/fulfill")
    assert response.status_code == 409


def test_cancel_pending_order(client: TestClient) -> None:
    create = client.post(
        "/orders",
        json={"customer_id": "cust-1", "items": [{"book_id": "b1", "quantity": 1}]},
    )
    order_id = create.json()["id"]

    cancel = client.post(f"/orders/{order_id}/cancel", json={"reason": "duplicate"})
    assert cancel.status_code == 200
    body = cancel.json()
    assert body["status"] == "CANCELLED"
    assert body["cancel_reason"] == "duplicate"


def test_list_orders_by_customer(client: TestClient) -> None:
    client.post("/orders", json={"customer_id": "cust-A", "items": [{"book_id": "b1", "quantity": 1}]})
    client.post("/orders", json={"customer_id": "cust-A", "items": [{"book_id": "b1", "quantity": 2}]})
    client.post("/orders", json={"customer_id": "cust-B", "items": [{"book_id": "b1", "quantity": 1}]})

    response = client.get("/orders", params={"customer_id": "cust-A"})
    assert response.status_code == 200
    assert len(response.json()) == 2
