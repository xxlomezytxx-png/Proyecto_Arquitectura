import logging
from typing import Optional

import httpx

from app.config import settings
from app.domain.entities.enrichment import BookMetadata, EnrichmentSource
from app.infrastructure.adapters.base_adapter import CircuitBreaker, SimpleCache, fetch_with_retry

logger = logging.getLogger(__name__)

_circuit_breaker = CircuitBreaker("crossref")
_cache = SimpleCache(ttl_seconds=3600)

TIMEOUT = 5.0


async def search_works(query: str) -> list[BookMetadata]:
    if _circuit_breaker.is_open():
        return []

    cache_key = f"crossref_{query[:60]}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        url = f"{settings.CROSSREF_BASE_URL}/works"
        params = {"query": query, "rows": 5, "select": "title,author,publisher,published-print,ISBN"}
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            async def _call() -> dict:
                r = await client.get(url, params=params)
                r.raise_for_status()
                return r.json()
            data = await fetch_with_retry(_call)

        items = data.get("message", {}).get("items", [])
        results = [_parse_work(item) for item in items]
        _cache.set(cache_key, results)
        _circuit_breaker.record_success()
        return results

    except Exception as exc:
        logger.error("Crossref search failed: %s", exc)
        _circuit_breaker.record_failure()
        return []


def _parse_work(item: dict) -> BookMetadata:
    titles = item.get("title", [])
    title = titles[0] if titles else None
    authors = item.get("author", [])
    author_parts = []
    for a in authors:
        name = f"{a.get('given', '')} {a.get('family', '')}".strip()
        if name:
            author_parts.append(name)
    author_str = "; ".join(author_parts) if author_parts else None

    pub_year = None
    published = item.get("published-print", {}).get("date-parts", [[None]])
    if published and published[0] and published[0][0]:
        pub_year = published[0][0]

    isbns = item.get("ISBN", [])
    isbn = isbns[0] if isbns else None

    return BookMetadata(
        title=title,
        author=author_str,
        publisher=item.get("publisher"),
        isbn=isbn,
        publication_year=pub_year,
        source=EnrichmentSource.crossref,
        confidence_score=0.75,
    )


def get_status() -> dict:
    return {
        "name": "crossref",
        "circuit_open": _circuit_breaker.is_open(),
        "failures": _circuit_breaker._failures,
    }
