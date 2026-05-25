import datetime
import enum

from sqlalchemy import Column, DateTime, Enum as SAEnum, Float, Integer, JSON, String, Text

from app.infrastructure.database.connection import Base


class EnrichmentStatusDB(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class EnrichmentRequestModel(Base):
    __tablename__ = "enrichment_requests"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(String(100), nullable=False, index=True)
    isbn = Column(String(100), nullable=True, index=True)
    title = Column(String(500), nullable=True)
    author = Column(String(300), nullable=True)
    publisher = Column(String(300), nullable=True)
    status = Column(SAEnum(EnrichmentStatusDB), default=EnrichmentStatusDB.pending)
    requested_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    source_used = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)


class EnrichmentResultModel(Base):
    __tablename__ = "enrichment_results"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, nullable=False, index=True)
    normalized_title = Column(String(500), nullable=True)
    normalized_author = Column(String(300), nullable=True)
    normalized_publisher = Column(String(300), nullable=True)
    normalized_description = Column(Text, nullable=True)
    cover_url = Column(String(1000), nullable=True)
    confidence_score = Column(Float, default=0.0)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
