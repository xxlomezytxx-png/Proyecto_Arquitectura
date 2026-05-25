import logging
from typing import Optional

import httpx

from app.config import settings
from app.domain.entities.enrichment import BookMetadata, EnrichmentSource
from app.infrastructure.adapters.base_adapter import CircuitBreaker, SimpleCache, fetch_with_retry

logger = logging.getLogger(__name__)

_circuit_breaker = CircuitBreaker("open_library")
_cache = SimpleCache(ttl_seconds=3600)

TIMEOUT = 5.0


async def get_by_isbn(isbn: str) -> Optional[BookMetadata]:
    if _circuit_breaker.is_open():
        return None

    cache_key = f"ol_isbn_{isbn}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        url = f"{settings.OPEN_LIBRARY_BASE_URL}/api/books"
        params = {"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"}
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            async def _call() -> dict:
                r = await client.get(url, params=params)
                r.raise_for_status()
                return r.json()
            data = await fetch_with_retry(_call)

        book_data = data.get(f"ISBN:{isbn}")
        if not book_data:
            _circuit_breaker.record_success()
            return None

        result = _parse_book(book_data)
        _cache.set(cache_key, result)
        _circuit_breaker.record_success()
        return result

    except Exception as exc:
        logger.error("Open Library ISBN lookup failed: %s", exc)
        _circuit_breaker.record_failure()
        return None


async def search(query: str) -> list[BookMetadata]:
    if _circuit_breaker.is_open():
        return []

    cache_key = f"ol_search_{query[:60]}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        url = f"{settings.OPEN_LIBRARY_BASE_URL}/search.json"
        params = {"q": query, "limit": 5}
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            async def _call() -> dict:
                r = await client.get(url, params=params)
                r.raise_for_status()
                return r.json()
            data = await fetch_with_retry(_call)

        results = [_parse_search_doc(doc) for doc in data.get("docs", [])[:5]]
        _cache.set(cache_key, results)
        _circuit_breaker.record_success()
        return results

    except Exception as exc:
        logger.error("Open Library search failed: %s", exc)
        _circuit_breaker.record_failure()
        return []


def _parse_book(data: dict) -> BookMetadata:
    authors = data.get("authors", [])
    author_str = "; ".join(a.get("name", "") for a in authors) if authors else None
    cover = None
    cover_data = data.get("cover", {})
    if cover_data:
        cover = cover_data.get("large") or cover_data.get("medium") or cover_data.get("small")

    return BookMetadata(
        title=data.get("title"),
        author=author_str,
        publisher=", ".join(p.get("name", "") for p in data.get("publishers", [])) or None,
        description=data.get("notes", {}).get("value") if isinstance(data.get("notes"), dict) else None,
        cover_url=cover,
        source=EnrichmentSource.open_library,
        confidence_score=0.8,
    )


def _parse_search_doc(doc: dict) -> BookMetadata:
    authors = doc.get("author_name", [])
    return BookMetadata(
        title=doc.get("title"),
        author="; ".join(authors) if authors else None,
        publisher=doc.get("publisher", [None])[0] if doc.get("publisher") else None,
        source=EnrichmentSource.open_library,
        confidence_score=0.7,
    )


def get_status() -> dict:
    return {
        "name": "open_library",
        "circuit_open": _circuit_breaker.is_open(),
        "failures": _circuit_breaker._failures,
    }
