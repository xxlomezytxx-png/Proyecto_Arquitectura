import datetime

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class CategoryModel(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)


class BookModel(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    subtitle = Column(String(500), nullable=True)
    author = Column(String(300), nullable=False, index=True)
    publisher = Column(String(300), nullable=True)
    publication_year = Column(Integer, nullable=True)
    volume = Column(String(50), nullable=True)
    # PostgreSQL allows multiple NULLs in a unique index, so unique=True is safe
    # for nullable ISBN/ISSN columns.
    isbn = Column(String(100), nullable=True, unique=True, index=True)
    issn = Column(String(100), nullable=True, unique=True)
    category_id = Column(Integer, nullable=True, index=True)
    description = Column(Text, nullable=True)
    cover_url = Column(String(500), nullable=True)

    price = Column(Integer, nullable=True)
    condition = Column(String(100), nullable=True)
    stock = Column(Integer, nullable=True)

    enriched_flag = Column(Boolean, default=False, index=True)
    published_flag = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()