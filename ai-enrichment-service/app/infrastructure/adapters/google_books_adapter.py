import logging
from typing import Optional

import httpx

from app.config import settings
from app.domain.entities.enrichment import BookMetadata, EnrichmentSource
from app.infrastructure.adapters.base_adapter import CircuitBreaker, SimpleCache, fetch_with_retry

logger = logging.getLogger(__name__)

_circuit_breaker = CircuitBreaker("google_books")
_cache = SimpleCache(ttl_seconds=3600)

BASE_URL = "https://www.googleapis.com/books/v1/volumes"
TIMEOUT = 5.0


async def search_by_isbn(isbn: str) -> Optional[BookMetadata]:
    if _circuit_breaker.is_open():
        logger.warning("Google Books circuit breaker is open, skipping")
        return None

    cache_key = f"google_isbn_{isbn}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        params = {"q": f"isbn:{isbn}"}
        if settings.GOOGLE_BOOKS_API_KEY:
            params["key"] = settings.GOOGLE_BOOKS_API_KEY
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            async def _call() -> dict:
                r = await client.get(BASE_URL, params=params)
                r.raise_for_status()
                return r.json()
            data = await fetch_with_retry(_call)

        items = data.get("items", [])
        if not items:
            _circuit_breaker.record_success()
            return None

        result = _parse_volume(items[0])
        _cache.set(cache_key, result)
        _circuit_breaker.record_success()
        return result

    except Exception as exc:
        logger.error("Google Books ISBN search failed: %s", exc)
        _circuit_breaker.record_failure()
        return None


async def search_by_title_author(title: str, author: str) -> list[BookMetadata]:
    if _circuit_breaker.is_open():
        return []

    cache_key = f"google_title_{title[:50]}_{author[:30]}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        query = f"intitle:{title}"
        if author:
            query += f"+inauthor:{author}"
        params = {"q": query, "maxResults": 5}
        if settings.GOOGLE_BOOKS_API_KEY:
            params["key"] = settings.GOOGLE_BOOKS_API_KEY
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            async def _call() -> dict:
                r = await client.get(BASE_URL, params=params)
                r.raise_for_status()
                return r.json()
            data = await fetch_with_retry(_call)

        results = [_parse_volume(item) for item in data.get("items", [])]
        _cache.set(cache_key, results)
        _circuit_breaker.record_success()
        return results

    except Exception as exc:
        logger.error("Google Books title search failed: %s", exc)
        _circuit_breaker.record_failure()
        return []


def _parse_volume(item: dict) -> BookMetadata:
    info = item.get("volumeInfo", {})
    authors = info.get("authors", [])
    author_str = "; ".join(authors) if authors else None
    image_links = info.get("imageLinks", {})
    cover = image_links.get("thumbnail") or image_links.get("smallThumbnail")
    pub_year = None
    published_date = info.get("publishedDate", "")
    if published_date and len(published_date) >= 4:
        try:
            pub_year = int(published_date[:4])
        except ValueError:
            pass

    return BookMetadata(
        title=info.get("title"),
        author=author_str,
        publisher=info.get("publisher"),
        description=info.get("description"),
        cover_url=cover,
        isbn=_extract_isbn(info.get("industryIdentifiers", [])),
        publication_year=pub_year,
        source=EnrichmentSource.google_books,
        confidence_score=0.9,
    )


def _extract_isbn(identifiers: list) -> Optional[str]:
    for ident in identifiers:
        if ident.get("type") == "ISBN_13":
            return ident.get("identifier")
    for ident in identifiers:
        if ident.get("type") == "ISBN_10":
            return ident.get("identifier")
    return None


def get_status() -> dict:
    return {
        "name": "google_books",
        "circuit_open": _circuit_breaker.is_open(),
        "failures": _circuit_breaker._failures,
    }
