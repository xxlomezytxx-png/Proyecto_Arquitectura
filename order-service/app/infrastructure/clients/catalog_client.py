from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.domain.interfaces.catalog_client import CatalogBook, CatalogClient
from app.infrastructure.clients.errors import UpstreamServiceError

logger = logging.getLogger(__name__)


class HttpCatalogClient(CatalogClient):
    def __init__(self, base_url: str, timeout: float = 5.0, client: Optional[httpx.AsyncClient] = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = client

    async def get_book(self, book_id: str) -> Optional[CatalogBook]:
        try:
            book_id_int = int(book_id)
        except (ValueError, TypeError) as exc:
            raise UpstreamServiceError(
                "catalog-service", f"book_id '{book_id}' is not a valid integer"
            ) from exc
        url = f"{self._base_url}/products/{book_id_int}"
        try:
            if self._client is not None:
                response = await self._client.get(url, timeout=self._timeout)
            else:
                async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                    response = await client.get(url)
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            logger.error("catalog-service unreachable: %s", exc)
            raise UpstreamServiceError("catalog-service", str(exc)) from exc

        if response.status_code == 404:
            return None
        if response.status_code >= 500:
            raise UpstreamServiceError(
                "catalog-service", f"HTTP {response.status_code}"
            )
        if response.status_code != 200:
            raise UpstreamServiceError(
                "catalog-service",
                f"unexpected HTTP {response.status_code}: {response.text[:200]}",
            )

        payload = response.json()
        return CatalogBook(
            book_id=str(payload.get("id", book_id)),
            title=str(payload.get("title", "")),
            author=payload.get("author"),
            isbn=payload.get("isbn"),
            is_published=bool(payload.get("published_flag", True)),
        )
