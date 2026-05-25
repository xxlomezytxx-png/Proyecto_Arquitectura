import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class CatalogClient:
    def __init__(self) -> None:
        self._base_url = settings.CATALOG_SERVICE_URL
        self._timeout = settings.HTTP_TIMEOUT

    def get_book(self, book_id: str) -> dict | None:
        try:
            with httpx.Client(timeout=self._timeout, follow_redirects=True) as client:
                resp = client.get(f"{self._base_url}/products/{book_id}")
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.warning("catalog get_book failed: %s", exc)
            return None

    def list_books(self, limit: int = 100) -> list[dict]:
        try:
            with httpx.Client(timeout=self._timeout, follow_redirects=True) as client:
                resp = client.get(f"{self._base_url}/products/", params={"limit": limit})
                resp.raise_for_status()
                data = resp.json()
                return data.get("items", data) if isinstance(data, dict) else data
        except Exception as exc:
            logger.warning("catalog list_books failed: %s", exc)
            return []
