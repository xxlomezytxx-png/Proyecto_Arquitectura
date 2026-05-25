import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class CatalogClient:
    def __init__(self) -> None:
        self._base_url = settings.CATALOG_SERVICE_URL
        self._timeout = settings.HTTP_TIMEOUT

    def _parse(self, data: object) -> list[dict]:
        if isinstance(data, dict):
            return data.get("items", data.get("data", []))
        if isinstance(data, list):
            return data
        return []

    def list_books(self, limit: int = 20) -> list[dict]:
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.get(f"{self._base_url}/products/", params={"limit": limit})
                resp.raise_for_status()
                return self._parse(resp.json())
        except Exception as exc:
            logger.warning("catalog list_books failed: %s", exc)
            return []

    def search_books(self, query: str, limit: int = 5) -> list[dict]:
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.get(
                    f"{self._base_url}/products/search",
                    params={"q": query, "limit": limit},
                )
                resp.raise_for_status()
                return self._parse(resp.json())
        except Exception as exc:
            logger.warning("catalog search failed: %s", exc)
            return []

    def get_book(self, book_id: str) -> dict | None:
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.get(f"{self._base_url}/products/{book_id}")
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.warning("catalog get_book failed: %s", exc)
            return None
