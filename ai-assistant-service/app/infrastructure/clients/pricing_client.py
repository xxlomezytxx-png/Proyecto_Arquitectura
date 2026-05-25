import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class PricingClient:
    def __init__(self) -> None:
        self._base_url = settings.PRICING_SERVICE_URL
        self._timeout = settings.HTTP_TIMEOUT

    def get_price(self, book_id: str) -> dict | None:
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.get(f"{self._base_url}/pricing/{book_id}")
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.warning("pricing get_price failed: %s", exc)
            return None
