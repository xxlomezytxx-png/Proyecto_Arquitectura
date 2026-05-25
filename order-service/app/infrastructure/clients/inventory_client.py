from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.domain.interfaces.inventory_client import InventoryClient, StockLevel
from app.infrastructure.clients.errors import UpstreamServiceError

logger = logging.getLogger(__name__)


class HttpInventoryClient(InventoryClient):
    def __init__(self, base_url: str, timeout: float = 5.0, client: Optional[httpx.AsyncClient] = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = client

    async def get_stock(self, book_id: str) -> StockLevel:
        url = f"{self._base_url}/inventory/availability/{book_id}"
        try:
            if self._client is not None:
                response = await self._client.get(url, timeout=self._timeout)
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.get(url)
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            logger.error("inventory-service unreachable: %s", exc)
            raise UpstreamServiceError("inventory-service", str(exc)) from exc

        if response.status_code == 404:
            return StockLevel(book_id=book_id, available=0)
        if response.status_code >= 500:
            raise UpstreamServiceError(
                "inventory-service", f"HTTP {response.status_code}"
            )
        if response.status_code != 200:
            raise UpstreamServiceError(
                "inventory-service",
                f"unexpected HTTP {response.status_code}: {response.text[:200]}",
            )

        payload = response.json()
        available = int(
            payload.get("quantity_available")
            or payload.get("stock")
            or payload.get("quantity")
            or 0
        )
        return StockLevel(book_id=str(payload.get("book_reference", book_id)), available=available)

    async def reserve_stock(self, book_id: str, quantity: int) -> None:
        url = f"{self._base_url}/inventory/availability/{book_id}/reserve"
        try:
            if self._client is not None:
                response = await self._client.patch(url, json={"quantity": quantity}, timeout=self._timeout)
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.patch(url, json={"quantity": quantity})
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            logger.error("inventory-service unreachable during reserve: %s", exc)
            raise UpstreamServiceError("inventory-service", str(exc)) from exc

        if response.status_code == 409:
            raise UpstreamServiceError("inventory-service", "Insufficient stock during reservation")
        if response.status_code >= 400:
            raise UpstreamServiceError(
                "inventory-service", f"reserve failed HTTP {response.status_code}: {response.text[:200]}"
            )
