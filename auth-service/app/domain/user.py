from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


@dataclass
class User:
    id: Optional[int]
    username: str
    email: str
    hashed_password: str
    role: UserRole
    is_active: bool
    created_at: Optional[datetime]

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
