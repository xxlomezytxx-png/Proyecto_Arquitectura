import datetime
import enum

from sqlalchemy import (Boolean, Column, DateTime, Enum as SAEnum,
                        Integer, String, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserRoleDB(str, enum.Enum):
    admin = "admin"
    user = "user"


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRoleDB), default=UserRoleDB.user, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))


class RevokedTokenModel(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(50), unique=True, index=True, nullable=False)
    revoked_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
