import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class InventoryClient:
    def __init__(self) -> None:
        self._base_url = settings.INVENTORY_SERVICE_URL
        self._timeout = settings.HTTP_TIMEOUT

    def list_items(self, limit: int = 50) -> list[dict]:
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.get(f"{self._base_url}/inventory/", params={"limit": limit})
                resp.raise_for_status()
                data = resp.json()
                return data if isinstance(data, list) else data.get("items", [])
        except Exception as exc:
            logger.warning("inventory list_items failed: %s", exc)
            return []

    def get_availability(self, book_id: str) -> dict | None:
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.get(f"{self._base_url}/inventory/availability/{book_id}")
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.warning("inventory get_availability failed: %s", exc)
            return None
