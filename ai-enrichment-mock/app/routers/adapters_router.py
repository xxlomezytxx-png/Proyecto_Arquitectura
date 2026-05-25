from fastapi import APIRouter, Query, HTTPException
from app.infrastructure.adapters import (
    get_all_adapters_status,
    google_books_client,
    open_library_client,
    CircuitBreakerOpenException
)

router = APIRouter()


@router.get("/status")
def get_adapters_status():
    """
    Returns the current status of all external API adapters, including circuit breaker state,
    failure counts, and cache size.
    """
    return get_all_adapters_status()

@router.get("/test/google-books")
def test_google_books(isbn: str = Query(..., description="ISBN to search")):
    """Test endpoint for Google Books Adapter"""
    try:
        return google_books_client.search_by_isbn(isbn)
    except CircuitBreakerOpenException as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test/open-library")
def test_open_library(query: str = Query(..., description="Query to search")):
    """Test endpoint for Open Library Adapter"""
    try:
        return open_library_client.search_by_query(query)
    except CircuitBreakerOpenException as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
