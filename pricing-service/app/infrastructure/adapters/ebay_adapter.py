import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
import httpx
from cachetools import TTLCache
from circuitbreaker import circuit

from app.config import settings
from app.domain.pricing import PricingReference

_RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


@dataclass
class EbayPriceResult:
    """Lightweight result returned by search_prices."""
    price: float
    currency: str
    title: str
    confidence_score: float


async def search_prices(isbn: str, title: Optional[str] = None) -> List[EbayPriceResult]:
    """
    Search eBay for price references.  Returns a list of EbayPriceResult.
    Falls back to an empty list on any error so the caller can apply
    internal-rules fallback without crashing.
    """
    if not settings.EBAY_APP_ID:
        return []

    query = isbn if isbn else title or ""
    if not query:
        return []

    params = {
        "q": f'"{query}" book',
        "category_ids": "267",
        "limit": "10",
        "sort": "price",
    }
    headers = {
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        "X-EBAY-C-ENDUSERCTX": f"affiliateCampaignId={settings.EBAY_APP_ID}",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            last_exc: BaseException = RuntimeError("no attempts")
            data: Dict[str, Any] = {}
            for attempt in range(3):
                try:
                    response = await client.get(settings.EBAY_API_URL, params=params, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    break
                except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
                    last_exc = exc
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code in _RETRYABLE_STATUS and attempt < 2:
                        last_exc = exc
                        await asyncio.sleep(2 ** attempt)
                    else:
                        raise
            else:
                raise last_exc

        results: List[EbayPriceResult] = []
        for item in data.get("itemSummaries", [])[:10]:
            price_info = item.get("price", {})
            value = price_info.get("value")
            if not value:
                continue
            results.append(
                EbayPriceResult(
                    price=float(value),
                    currency=price_info.get("currency", "USD"),
                    title=item.get("title", ""),
                    confidence_score=1.0,
                )
            )
        return results
    except Exception:
        return []


class ExternalAPIStatus:
    def __init__(self):
        self.last_check = datetime.now(timezone.utc)
        self.is_available = True
        self.error_message = None

    def update_status(self, available: bool, error: str = None):
        self.last_check = datetime.now(timezone.utc)
        self.is_available = available
        self.error_message = error


class EbayAdapter:
    def __init__(self):
        self.cache = TTLCache(maxsize=100, ttl=settings.CACHE_TTL)
        self.status = ExternalAPIStatus()
        self.client = httpx.AsyncClient(timeout=10.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    @circuit(failure_threshold=settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
             recovery_timeout=settings.CIRCUIT_BREAKER_RECOVERY_TIMEOUT)
    async def get_book_prices(self, book_title: str, author: str = None) -> List[PricingReference]:
        """Get pricing references from eBay API"""
        if not settings.EBAY_APP_ID:
            return []

        cache_key = f"{book_title}_{author or ''}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Build search query
            query = f'"{book_title}"'
            if author:
                query += f' "{author}"'

            params = {
                'q': query,
                'category_ids': '267',  # Books category
                'limit': '20',
                'sort': 'price'
            }

            headers = {
                'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
                'X-EBAY-C-ENDUSERCTX': f'affiliateCampaignId={settings.EBAY_APP_ID}'
            }

            last_exc: BaseException = RuntimeError("no attempts")
            data: Dict[str, Any] = {}
            for attempt in range(3):
                try:
                    response = await self.client.get(
                        settings.EBAY_API_URL,
                        params=params,
                        headers=headers,
                    )
                    response.raise_for_status()
                    data = response.json()
                    break
                except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
                    last_exc = exc
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code in _RETRYABLE_STATUS and attempt < 2:
                        last_exc = exc
                        await asyncio.sleep(2 ** attempt)
                    else:
                        raise
            else:
                raise last_exc

            references = self._parse_ebay_response(data, book_title)
            self.cache[cache_key] = references
            self.status.update_status(True)
            return references

        except Exception as e:
            self.status.update_status(False, str(e))
            raise

    def _parse_ebay_response(self, data: Dict[str, Any], book_title: str) -> List[PricingReference]:
        """Parse eBay API response into PricingReference objects"""
        references = []

        if 'itemSummaries' not in data:
            return references

        for item in data['itemSummaries'][:10]:  # Limit to 10 references
            try:
                price_info = item.get('price', {})
                if not price_info:
                    continue

                # Extract price
                value = price_info.get('value')
                currency = price_info.get('currency', 'USD')

                if not value:
                    continue

                price = float(value)

                # Create reference
                reference = PricingReference(
                    id=None,
                    book_id=book_title,  # Using title as book_id for simplicity
                    source="eBay",
                    price=price,
                    currency=currency,
                    observed_at=datetime.now(timezone.utc),
                    metadata={
                        'item_id': item.get('itemId'),
                        'title': item.get('title'),
                        'condition': item.get('condition'),
                        'seller': item.get('seller', {}).get('username'),
                        'url': item.get('itemWebUrl')
                    }
                )
                references.append(reference)

            except (ValueError, KeyError):
                continue

        return references

    def get_status(self) -> Dict[str, Any]:
        """Get current status of eBay API"""
        return {
            'source': 'eBay',
            'available': self.status.is_available,
            'last_check': self.status.last_check.isoformat(),
            'error_message': self.status.error_message
        }


# For testing/development, create a mock adapter
class MockEbayAdapter(EbayAdapter):
    async def get_book_prices(self, book_title: str, author: str = None) -> List[PricingReference]:
        """Mock implementation for testing"""
        cache_key = f"{book_title}_{author or ''}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        # Simulate some delay
        await asyncio.sleep(0.1)

        # Mock data
        mock_prices = [15.99, 12.50, 18.75, 10.00, 22.99]
        references = []

        for i, price in enumerate(mock_prices):
            reference = PricingReference(
                id=None,
                book_id=book_title,
                source="eBay",
                price=price,
                currency="USD",
                observed_at=datetime.now(timezone.utc),
                metadata={
                    'item_id': f'mock_{i}',
                    'title': f"{book_title} - Copy {i+1}",
                    'condition': 'Used' if i % 2 == 0 else 'New',
                    'seller': f'seller_{i}',
                    'url': f'https://ebay.com/item/mock_{i}'
                }
            )
            references.append(reference)

        self.cache[cache_key] = references
        self.status.update_status(True)
        return references
