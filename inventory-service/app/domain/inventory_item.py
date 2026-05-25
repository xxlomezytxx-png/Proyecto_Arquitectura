from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class ItemCondition(str, Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"


class DefectType(str, Enum):
    TORN_PAGES = "torn_pages"
    WATER_DAMAGE = "water_damage"
    WRITING = "writing"
    HIGHLIGHTING = "highlighting"
    COVER_DAMAGE = "cover_damage"
    MISSING_PAGES = "missing_pages"
    SPINE_DAMAGE = "spine_damage"
    STAINS = "stains"
    OTHER = "other"


@dataclass(frozen=True)
class Defect:
    type: DefectType
    description: Optional[str] = None


class BatchStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class InventoryItem:
    id: Optional[int]
    external_code: Optional[str]
    book_reference: str
    title: str
    isbn: Optional[str]
    quantity_available: int
    quantity_reserved: int
    condition: ItemCondition
    author: str = ""
    defects: List[Defect] = field(default_factory=list)
    observations: Optional[str] = None
    import_batch_id: Optional[int] = None
    created_at: Optional[datetime] = None

    def is_available(self) -> bool:
        return self.quantity_available > 0

    def validate(self) -> List[str]:
        errors = []
        if not self.book_reference or not self.book_reference.strip():
            errors.append("book_reference es requerido")
        if not self.title or not self.title.strip():
            errors.append("title es requerido")
        if self.quantity_available < 0:
            errors.append("quantity_available no puede ser negativo")
        return errors


@dataclass
class ImportBatch:
    id: Optional[int]
    file_name: str
    upload_date: Optional[datetime]
    processed_rows: int
    valid_rows: int
    invalid_rows: int
    status: BatchStatus


@dataclass
class ImportError:
    id: Optional[int]
    batch_id: int
    row_number: int
    error_type: str
    message: str
    raw_data: Optional[str]
