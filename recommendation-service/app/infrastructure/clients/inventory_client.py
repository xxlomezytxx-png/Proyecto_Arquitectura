import logging
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class InventoryClient:
    def __init__(self) -> None:
        self._base_url = settings.INVENTORY_SERVICE_URL
        self._timeout = settings.HTTP_TIMEOUT

    def is_available(self, book_id: str) -> bool:
        try:
            with httpx.Client(timeout=self._timeout, follow_redirects=True) as client:
                resp = client.get(f"{self._base_url}/inventory/{book_id}")
                if resp.status_code == 404:
                    return False
                resp.raise_for_status()
                data = resp.json()
                return data.get("quantity", 0) > 0
        except Exception as exc:
            logger.warning("inventory is_available failed: %s", exc)
            return True