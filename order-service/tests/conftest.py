"""Test fixtures. Overrides DATABASE_URL to in-memory sqlite before any
app module imports so the engine is built against the test DB."""
from __future__ import annotations

import os
from typing import Iterator

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("HTTP_TIMEOUT", "1.0")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Fresh in-memory sqlite per test, with all tables created."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    from app.infrastructure.database.connection import Base
    from app.infrastructure.database import models  # noqa: F401  registers tables

    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
