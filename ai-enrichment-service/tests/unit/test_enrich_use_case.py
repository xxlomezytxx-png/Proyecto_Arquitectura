import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.application.use_cases.enrich_book import EnrichBookUseCase
from app.domain.entities.enrichment import (BookMetadata, EnrichmentSource,
                                              EnrichmentStatus, EnrichmentRequest)
from datetime import datetime, timezone


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.save_request.return_value = EnrichmentRequest(
        id=1, book_id="book-1", isbn="9780141439518",
        title="Great Expectations", author="Dickens, Charles",
        publisher=None, status=EnrichmentStatus.pending,
        requested_at=datetime.now(timezone.utc),
    )
    repo.save_result.return_value = MagicMock(id=1, request_id=1)
    return repo


@pytest.mark.asyncio
async def test_enrich_by_isbn_google_books_success(mock_repo):
    metadata = BookMetadata(
        title="Great Expectations", author="Charles Dickens",
        publisher="Penguin", description="A novel.",
        cover_url="https://example.com/cover.jpg",
        source=EnrichmentSource.google_books, confidence_score=0.9,
    )
    with patch("app.application.use_cases.enrich_book.google_books_adapter.search_by_isbn",
               new=AsyncMock(return_value=metadata)):
        with patch("app.application.use_cases.enrich_book.google_books_adapter.search_by_title_author",
                   new=AsyncMock(return_value=[])):
            use_case = EnrichBookUseCase(mock_repo)
            result = await use_case.execute("book-1", "9780141439518", "Great Expectations", None, None)

    assert result["status"] == "completed"
    assert result["source_used"] == "google_books"
    assert "Great" in result["normalized_title"]


@pytest.mark.asyncio
async def test_enrich_fallback_when_google_fails(mock_repo):
    ol_metadata = BookMetadata(
        title="Great Expectations", author="Dickens",
        source=EnrichmentSource.open_library, confidence_score=0.8,
    )
    with patch("app.application.use_cases.enrich_book.google_books_adapter.search_by_isbn",
               new=AsyncMock(return_value=None)):
        with patch("app.application.use_cases.enrich_book.google_books_adapter.search_by_title_author",
                   new=AsyncMock(return_value=[])):
            with patch("app.application.use_cases.enrich_book.open_library_adapter.get_by_isbn",
                       new=AsyncMock(return_value=ol_metadata)):
                use_case = EnrichBookUseCase(mock_repo)
                result = await use_case.execute("book-1", "9780141439518", None, None, None)

    assert result["status"] == "completed"
    assert result["source_used"] == "open_library"


@pytest.mark.asyncio
async def test_enrich_all_sources_fail_returns_partial(mock_repo):
    with patch("app.application.use_cases.enrich_book.google_books_adapter.search_by_isbn",
               new=AsyncMock(return_value=None)):
        with patch("app.application.use_cases.enrich_book.google_books_adapter.search_by_title_author",
                   new=AsyncMock(return_value=[])):
            with patch("app.application.use_cases.enrich_book.open_library_adapter.get_by_isbn",
                       new=AsyncMock(return_value=None)):
                with patch("app.application.use_cases.enrich_book.open_library_adapter.search",
                           new=AsyncMock(return_value=[])):
                    with patch("app.application.use_cases.enrich_book.crossref_adapter.search_works",
                               new=AsyncMock(return_value=[])):
                        use_case = EnrichBookUseCase(mock_repo)
                        result = await use_case.execute("book-1", "9780141439518",
                                                        "Great Expectations", None, None)

    assert result["status"] == "failed"
    assert result["source_used"] == "none"


@pytest.mark.asyncio
async def test_normalization_merges_fields_correctly(mock_repo):
    google = BookMetadata(title="great expectations", author="Charles Dickens",
                          source=EnrichmentSource.google_books, confidence_score=0.9)
    ol = BookMetadata(title=None, description="Classic novel",
                      cover_url="https://example.com/img.jpg",
                      source=EnrichmentSource.open_library, confidence_score=0.7)
    with patch("app.application.use_cases.enrich_book.google_books_adapter.search_by_isbn",
               new=AsyncMock(return_value=None)):
        with patch("app.application.use_cases.enrich_book.google_books_adapter.search_by_title_author",
                   new=AsyncMock(return_value=[google, ol])):
            use_case = EnrichBookUseCase(mock_repo)
            result = await use_case.execute("book-1", None, "great expectations", None, None)

    assert result["status"] == "completed"
    # Normalized title should be title-cased
    assert result["normalized_title"] == "Great Expectations"
    assert result["cover_url"] == "https://example.com/img.jpg"
