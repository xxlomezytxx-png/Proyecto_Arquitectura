from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.enrichment import (EnrichmentRequest, EnrichmentResult,
                                              EnrichmentSource, EnrichmentStatus)
from app.domain.interfaces.enrichment_repository import EnrichmentRepositoryInterface
from app.infrastructure.database.models import (EnrichmentRequestModel,
                                                  EnrichmentResultModel,
                                                  EnrichmentStatusDB)


class EnrichmentRepository(EnrichmentRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def save_request(self, book_id: str, isbn: Optional[str], title: Optional[str],
                     author: Optional[str], publisher: Optional[str]) -> EnrichmentRequest:
        model = EnrichmentRequestModel(
            book_id=book_id,
            isbn=isbn,
            title=title,
            author=author,
            publisher=publisher,
            status=EnrichmentStatusDB.pending,
            requested_at=datetime.now(timezone.utc),
        )
        self.db.add(model)
        try:
            self.db.commit()
            self.db.refresh(model)
        except Exception:
            self.db.rollback()
            raise
        return self._to_entity(model)

    def update_request_status(self, request_id: int, status: str,
                               source_used: Optional[str] = None,
                               error_message: Optional[str] = None) -> None:
        model = self.db.query(EnrichmentRequestModel).filter(
            EnrichmentRequestModel.id == request_id
        ).first()
        if model:
            model.status = status
            if source_used is not None:
                model.source_used = source_used
            if error_message is not None:
                model.error_message = error_message
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise

    def get_request(self, request_id: int) -> Optional[EnrichmentRequest]:
        model = self.db.query(EnrichmentRequestModel).filter(
            EnrichmentRequestModel.id == request_id
        ).first()
        return self._to_entity(model) if model else None

    def save_result(self, request_id: int, title: Optional[str], author: Optional[str],
                    publisher: Optional[str], description: Optional[str],
                    cover_url: Optional[str], confidence_score: float) -> EnrichmentResult:
        model = EnrichmentResultModel(
            request_id=request_id,
            normalized_title=title,
            normalized_author=author,
            normalized_publisher=publisher,
            normalized_description=description,
            cover_url=cover_url,
            confidence_score=confidence_score,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(model)
        try:
            self.db.commit()
            self.db.refresh(model)
        except Exception:
            self.db.rollback()
            raise
        return self._to_result_entity(model)

    def get_result_by_request(self, request_id: int) -> Optional[EnrichmentResult]:
        model = self.db.query(EnrichmentResultModel).filter(
            EnrichmentResultModel.request_id == request_id
        ).first()
        return self._to_result_entity(model) if model else None

    def _to_entity(self, model: EnrichmentRequestModel) -> EnrichmentRequest:
        return EnrichmentRequest(
            id=model.id,
            book_id=model.book_id,
            isbn=model.isbn,
            title=model.title,
            author=model.author,
            publisher=model.publisher,
            status=EnrichmentStatus(model.status),
            requested_at=model.requested_at,
            source_used=model.source_used,
            error_message=model.error_message,
        )

    def _to_result_entity(self, model: EnrichmentResultModel) -> EnrichmentResult:
        return EnrichmentResult(
            id=model.id,
            request_id=model.request_id,
            normalized_title=model.normalized_title,
            normalized_author=model.normalized_author,
            normalized_publisher=model.normalized_publisher,
            normalized_description=model.normalized_description,
            cover_url=model.cover_url,
            confidence_score=model.confidence_score,
            created_at=model.created_at,
        )
