import pytest
from unittest.mock import MagicMock

from app.domain.entities.enrichment import (EnrichmentRequest, EnrichmentResult,
                                              EnrichmentStatus, EnrichmentSource)
from datetime import datetime, timezone


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.save_request.return_value = EnrichmentRequest(
        id=1, book_id="book-1", isbn="9780141439518",
        title="Great Expectations", author="Dickens, Charles",
        publisher="Penguin", status=EnrichmentStatus.pending,
        requested_at=datetime.now(timezone.utc),
    )
    repo.get_result_by_request.return_value = None
    return repo
