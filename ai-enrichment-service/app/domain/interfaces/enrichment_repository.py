from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.enrichment import EnrichmentRequest, EnrichmentResult


class EnrichmentRepositoryInterface(ABC):
    @abstractmethod
    def save_request(self, book_id: str, isbn: Optional[str], title: Optional[str],
                     author: Optional[str], publisher: Optional[str]) -> EnrichmentRequest:
        ...

    @abstractmethod
    def update_request_status(self, request_id: int, status: str,
                               source_used: Optional[str] = None,
                               error_message: Optional[str] = None) -> None:
        ...

    @abstractmethod
    def get_request(self, request_id: int) -> Optional[EnrichmentRequest]:
        ...

    @abstractmethod
    def save_result(self, request_id: int, title: Optional[str], author: Optional[str],
                    publisher: Optional[str], description: Optional[str],
                    cover_url: Optional[str], confidence_score: float) -> EnrichmentResult:
        ...

    @abstractmethod
    def get_result_by_request(self, request_id: int) -> Optional[EnrichmentResult]:
        ...
