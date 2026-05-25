from typing import Optional

from sqlalchemy.orm import Session

from app.domain.user import User, UserRole
from app.infrastructure.database import UserModel


def _to_domain(model: UserModel) -> User:
    return User(
        id=model.id,
        username=model.username,
        email=model.email,
        hashed_password=model.hashed_password,
        role=UserRole(model.role.value),
        is_active=model.is_active,
        created_at=model.created_at,
    )


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    model = db.query(UserModel).filter(UserModel.username == username).first()
    return _to_domain(model) if model else None


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    model = db.query(UserModel).filter(UserModel.email == email).first()
    return _to_domain(model) if model else None


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    model = db.query(UserModel).filter(UserModel.id == user_id).first()
    return _to_domain(model) if model else None


def create_user(db: Session, user: User) -> User:
    model = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=user.hashed_password,
        role=user.role.value,
        is_active=user.is_active,
    )
    db.add(model)
    try:
        db.commit()
        db.refresh(model)
    except Exception:
        db.rollback()
        raise
    return _to_domain(model)
