import logging
from typing import Optional

from app.application.normalizer.source_merger import merge_results
from app.domain.entities.enrichment import BookMetadata, EnrichmentSource, EnrichmentStatus
from app.domain.interfaces.enrichment_repository import EnrichmentRepositoryInterface
from app.infrastructure.adapters import (crossref_adapter, google_books_adapter,
                                          open_library_adapter)

logger = logging.getLogger(__name__)


class EnrichBookUseCase:
    def __init__(self, repository: EnrichmentRepositoryInterface):
        self.repository = repository

    async def execute(self, book_id: str, isbn: Optional[str], title: Optional[str],
                      author: Optional[str], publisher: Optional[str]) -> dict:
        # Persist the request
        req = self.repository.save_request(book_id, isbn, title, author, publisher)
        self.repository.update_request_status(req.id, EnrichmentStatus.processing)

        candidates: list[BookMetadata] = []

        # 1. Google Books (highest priority)
        if isbn:
            result = await google_books_adapter.search_by_isbn(isbn)
            if result:
                candidates.append(result)

        if not candidates and title:
            results = await google_books_adapter.search_by_title_author(title, author or "")
            candidates.extend(results)

        # 2. Open Library
        if isbn and not candidates:
            result = await open_library_adapter.get_by_isbn(isbn)
            if result:
                candidates.append(result)

        if not candidates and title:
            query = f"{title} {author or ''}".strip()
            results = await open_library_adapter.search(query)
            candidates.extend(results)

        # 3. Crossref fallback
        if not candidates and title:
            query = f"{title} {author or ''}".strip()
            results = await crossref_adapter.search_works(query)
            candidates.extend(results)

        if not candidates:
            self.repository.update_request_status(
                req.id, EnrichmentStatus.failed,
                source_used=EnrichmentSource.none.value,
                error_message="No results found from any source"
            )
            return {
                "request_id": req.id,
                "status": "failed",
                "source_used": "none",
                "normalized_title": title,
                "normalized_author": author,
                "normalized_publisher": publisher,
                "normalized_description": None,
                "cover_url": None,
                "confidence_score": 0.0,
            }

        merged = merge_results(candidates)
        result_entity = self.repository.save_result(
            request_id=req.id,
            title=merged.title,
            author=merged.author,
            publisher=merged.publisher,
            description=merged.description,
            cover_url=merged.cover_url,
            confidence_score=merged.confidence_score,
        )
        self.repository.update_request_status(
            req.id, EnrichmentStatus.completed,
            source_used=merged.source.value,
        )

        return {
            "request_id": req.id,
            "status": "completed",
            "normalized_title": merged.title,
            "normalized_author": merged.author,
            "normalized_publisher": merged.publisher,
            "normalized_description": merged.description,
            "cover_url": merged.cover_url,
            "source_used": merged.source.value,
            "confidence_score": merged.confidence_score,
        }
