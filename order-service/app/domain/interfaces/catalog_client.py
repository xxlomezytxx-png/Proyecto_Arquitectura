from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass(frozen=True)
class CatalogBook:
    book_id: str
    title: str
    author: Optional[str] = None
    isbn: Optional[str] = None
    is_published: bool = True


class CatalogClient(Protocol):
    """Port for book validation against catalog-service."""

    async def get_book(self, book_id: str) -> Optional[CatalogBook]: ...
