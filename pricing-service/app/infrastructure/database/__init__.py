import datetime
import enum
import json

from sqlalchemy import (Boolean, Column, DateTime, Enum as SAEnum,
                        Integer, String, Text, Float, JSON, create_engine, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from app.config import settings

Base = declarative_base()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class BookConditionDB(str, enum.Enum):
    NUEVO = "NUEVO"
    BUENO = "BUENO"
    ACEPTABLE = "ACEPTABLE"
    DETERIORADO = "DETERIORADO"


class PricingReferenceModel(Base):
    __tablename__ = "pricing_references"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(String(100), index=True, nullable=False)
    decision_id = Column(Integer, ForeignKey("pricing_decisions.id"), nullable=True, index=True)
    source = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    observed_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    extra_data = Column(JSON, default=dict)


class PricingDecisionModel(Base):
    __tablename__ = "pricing_decisions"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(String(100), index=True, nullable=False)
    book_title = Column(String(500), nullable=True)
    condition = Column(SAEnum(BookConditionDB), nullable=False)
    base_price = Column(Float, nullable=False)
    condition_factor = Column(Float, nullable=False)
    suggested_price = Column(Float, nullable=False)
    references_used = Column(Integer, nullable=False)
    source = Column(String(50), nullable=False)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    references = relationship("PricingReferenceModel", backref="decision")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
