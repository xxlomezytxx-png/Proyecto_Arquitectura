from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class EnrichmentStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class EnrichmentSource(str, Enum):
    google_books = "google_books"
    open_library = "open_library"
    crossref = "crossref"
    none = "none"


@dataclass
class BookMetadata:
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    isbn: Optional[str] = None
    publication_year: Optional[int] = None
    source: EnrichmentSource = EnrichmentSource.none
    confidence_score: float = 0.0


@dataclass
class EnrichmentRequest:
    id: int
    book_id: str
    isbn: Optional[str]
    title: Optional[str]
    author: Optional[str]
    publisher: Optional[str]
    status: EnrichmentStatus
    requested_at: datetime
    source_used: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class EnrichmentResult:
    id: int
    request_id: int
    normalized_title: Optional[str]
    normalized_author: Optional[str]
    normalized_publisher: Optional[str]
    normalized_description: Optional[str]
    cover_url: Optional[str]
    confidence_score: float
    created_at: datetime
