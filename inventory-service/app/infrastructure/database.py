import datetime
import enum

from sqlalchemy import (Boolean, Column, DateTime, Enum as SAEnum,
                        Integer, JSON, String, Text, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ItemConditionDB(str, enum.Enum):
    new = "new"
    like_new = "like_new"
    good = "good"
    acceptable = "acceptable"
    poor = "poor"


class BatchStatusDB(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class InventoryItemModel(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    external_code = Column(String(100), nullable=True)
    book_reference = Column(String(200), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    author = Column(String(300), nullable=False)
    isbn = Column(String(100), nullable=True, index=True)
    quantity_available = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    condition = Column(SAEnum(ItemConditionDB), default=ItemConditionDB.good)
    defects = Column(JSON, nullable=True)
    observations = Column(Text, nullable=True)
    import_batch_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))


class ImportBatchModel(Base):
    __tablename__ = "import_batches"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(300), nullable=False)
    upload_date = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    processed_rows = Column(Integer, default=0)
    valid_rows = Column(Integer, default=0)
    invalid_rows = Column(Integer, default=0)
    status = Column(SAEnum(BatchStatusDB), default=BatchStatusDB.pending)


class ImportErrorModel(Base):
    __tablename__ = "import_errors"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    error_type = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    raw_data = Column(Text, nullable=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
