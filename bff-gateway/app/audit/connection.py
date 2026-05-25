import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

AUDIT_DB_URL = os.getenv(
    "AUDIT_DATABASE_URL",
    "postgresql://bookflow:bookflow123@audit-db:5432/audit_db",
)

engine = create_engine(AUDIT_DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
