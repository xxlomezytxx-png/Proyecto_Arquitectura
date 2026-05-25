from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.book import Book, Category
from app.infrastructure import catalog_repository


def create_book(db: Session, **kwargs) -> Book:
    book = Book(
        id=None,
        enriched_flag=False,
        price=kwargs.pop("price", None),
        condition=kwargs.pop("condition", None),
        stock=kwargs.pop("stock", None),
        created_at=None,
        updated_at=None,
        **kwargs
    )

    errors = book.validate()
    if errors:
        raise ValueError(", ".join(errors))

    return catalog_repository.create_book(db, book)


def get_book(db: Session, book_id: int) -> Optional[Book]:
    return catalog_repository.get_book(db, book_id)


def list_books(db: Session, skip: int = 0, limit: int = 20, published_only: bool = False) -> List[Book]:
    return catalog_repository.get_all_books(db, skip, limit, published_only)


def search_books(db: Session, query: str, skip: int = 0, limit: int = 20) -> List[Book]:
    return catalog_repository.search_books(db, query, skip, limit)


def update_book(db: Session, book_id: int, **kwargs) -> Optional[Book]:
    return catalog_repository.update_book(db, book_id, **kwargs)


def delete_book(db: Session, book_id: int) -> bool:
    return catalog_repository.delete_book(db, book_id)


def publish_book(db: Session, book_id: int) -> Optional[Book]:
    book = catalog_repository.get_book(db, book_id)
    if not book:
        return None
    if not book.can_publish():
        raise ValueError("El libro necesita título, autor y al menos ISBN/ISSN/editorial para publicarse")
    return catalog_repository.update_book(db, book_id, published_flag=True)


def mark_enriched(db: Session, book_id: int) -> Optional[Book]:
    book = catalog_repository.get_book(db, book_id)
    if not book:
        return None
    return catalog_repository.update_book(db, book_id, enriched_flag=True)


def list_categories(db: Session) -> List[Category]:
    return catalog_repository.get_all_categories(db)


def create_category(db: Session, name: str, description: str = None) -> Category:
    return catalog_repository.create_category(db, name, description)