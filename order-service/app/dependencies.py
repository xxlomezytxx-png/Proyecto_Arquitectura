from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.cancel_order import CancelOrderUseCase
from app.application.use_cases.confirm_order import ConfirmOrderUseCase
from app.application.use_cases.create_order import CreateOrderUseCase
from app.application.use_cases.fulfill_order import FulfillOrderUseCase
from app.config import settings
from app.infrastructure.clients.catalog_client import HttpCatalogClient
from app.infrastructure.clients.inventory_client import HttpInventoryClient
from app.infrastructure.clients.pricing_client import HttpPricingClient
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.order_repository import \
    SqlAlchemyOrderRepository


def get_order_repository(db: Session = Depends(get_db)) -> SqlAlchemyOrderRepository:
    return SqlAlchemyOrderRepository(db)


def get_catalog_client() -> HttpCatalogClient:
    return HttpCatalogClient(settings.CATALOG_SERVICE_URL, timeout=settings.HTTP_TIMEOUT)


def get_inventory_client() -> HttpInventoryClient:
    return HttpInventoryClient(settings.INVENTORY_SERVICE_URL, timeout=settings.HTTP_TIMEOUT)


def get_pricing_client() -> HttpPricingClient:
    return HttpPricingClient(settings.PRICING_SERVICE_URL, timeout=settings.HTTP_TIMEOUT)


def get_create_order_use_case(
    repo: SqlAlchemyOrderRepository = Depends(get_order_repository),
    catalog: HttpCatalogClient = Depends(get_catalog_client),
    pricing: HttpPricingClient = Depends(get_pricing_client),
) -> CreateOrderUseCase:
    return CreateOrderUseCase(repo, catalog, pricing)


def get_confirm_order_use_case(
    repo: SqlAlchemyOrderRepository = Depends(get_order_repository),
    inventory: HttpInventoryClient = Depends(get_inventory_client),
) -> ConfirmOrderUseCase:
    return ConfirmOrderUseCase(repo, inventory)


def get_cancel_order_use_case(
    repo: SqlAlchemyOrderRepository = Depends(get_order_repository),
) -> CancelOrderUseCase:
    return CancelOrderUseCase(repo)


def get_fulfill_order_use_case(
    repo: SqlAlchemyOrderRepository = Depends(get_order_repository),
) -> FulfillOrderUseCase:
    return FulfillOrderUseCase(repo)
