from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.domain.interfaces.pricing_client import PriceQuote, PricingClient
from app.infrastructure.clients.errors import UpstreamServiceError

logger = logging.getLogger(__name__)


class HttpPricingClient(PricingClient):
    def __init__(self, base_url: str, timeout: float = 5.0, client: Optional[httpx.AsyncClient] = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = client

    async def get_latest_price(self, book_id: str) -> Optional[PriceQuote]:
        url = f"{self._base_url}/pricing/{book_id}"
        try:
            if self._client is not None:
                response = await self._client.get(url, timeout=self._timeout)
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.get(url)
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            raise UpstreamServiceError("pricing-service", str(exc)) from exc

        if response.status_code == 404:
            return None
        if response.status_code >= 500:
            raise UpstreamServiceError(
                "pricing-service", f"HTTP {response.status_code}"
            )
        if response.status_code != 200:
            return None

        payload = response.json()
        suggested = payload.get("suggested_price")
        if suggested is None:
            return None
        return PriceQuote(
            book_id=str(payload.get("book_id", book_id)),
            suggested_price=float(suggested),
            source=str(payload.get("source", "unknown")),
        )
