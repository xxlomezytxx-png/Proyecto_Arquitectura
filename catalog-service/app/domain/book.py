from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Category:
    id: Optional[int]
    name: str
    description: Optional[str]


@dataclass
class Book:
    id: Optional[int]
    title: str
    subtitle: Optional[str]
    author: str
    publisher: Optional[str]
    publication_year: Optional[int]
    volume: Optional[str]
    isbn: Optional[str]
    issn: Optional[str]
    category_id: Optional[int]
    description: Optional[str]
    cover_url: Optional[str]
    enriched_flag: bool
    published_flag: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    price: Optional[int] = None
    condition: Optional[str] = None
    stock: Optional[int] = None

    def validate(self) -> List[str]:
        errors = []
        if not self.title or not self.title.strip():
            errors.append("El título es requerido")
        if not self.author or not self.author.strip():
            errors.append("El autor es requerido")
        return errors

    def can_publish(self) -> bool:
        return bool(self.title and self.author and (self.isbn or self.issn or self.publisher))
