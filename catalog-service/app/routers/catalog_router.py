from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.catalog_use_cases import (
    create_book,
    delete_book,
    get_book,
    list_books,
    mark_enriched,
    publish_book,
    search_books,
    update_book,
)
from app.infrastructure.database import get_db

router = APIRouter()


class BookCreateRequest(BaseModel):
    title: str
    author: str
    subtitle: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    volume: Optional[str] = None
    isbn: Optional[str] = None
    issn: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    price: Optional[int] = None
    condition: Optional[str] = None
    stock: Optional[int] = None
    published_flag: bool = False


class BookUpdateRequest(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    subtitle: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    isbn: Optional[str] = None
    category_id: Optional[int] = None
    condition: Optional[str] = None
    stock: Optional[int] = None
    price: Optional[int] = None


class PriceUpdateRequest(BaseModel):
    price: float


class BookResponse(BaseModel):
    id: int
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
    price: Optional[int]
    condition: Optional[str]
    stock: Optional[int]
    enriched_flag: bool
    published_flag: bool
    created_at: Optional[datetime]


def _resp(b) -> BookResponse:
    return BookResponse(
        id=b.id,
        title=b.title,
        subtitle=b.subtitle,
        author=b.author,
        publisher=b.publisher,
        publication_year=b.publication_year,
        volume=b.volume,
        isbn=b.isbn,
        issn=b.issn,
        category_id=b.category_id,
        description=b.description,
        cover_url=b.cover_url,
        price=b.price,
        condition=b.condition,
        stock=b.stock,
        enriched_flag=b.enriched_flag,
        published_flag=b.published_flag,
        created_at=b.created_at,
    )


@router.post("/", response_model=BookResponse, status_code=201)
def create(req: BookCreateRequest, db: Session = Depends(get_db)):
    try:
        return _resp(create_book(db, **req.model_dump()))
    except ValueError as e:
        msg = str(e)
        status = 409 if "Ya existe un libro con el ISBN" in msg else 422
        raise HTTPException(status_code=status, detail=msg)


@router.get("/search", response_model=List[BookResponse])
def search(
    q: str = Query(..., min_length=2),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return [_resp(b) for b in search_books(db, q, skip, limit)]


@router.get("/", response_model=List[BookResponse])
def list_all(
    skip: int = 0,
    limit: int = 20,
    published_only: bool = False,
    db: Session = Depends(get_db),
):
    return [_resp(b) for b in list_books(db, skip, limit, published_only)]


@router.get("/{book_id}", response_model=BookResponse)
def get_one(book_id: int, db: Session = Depends(get_db)):
    b = get_book(db, book_id)
    if not b:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return _resp(b)


@router.put("/{book_id}", response_model=BookResponse)
def update_one(book_id: int, req: BookUpdateRequest, db: Session = Depends(get_db)):
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    b = update_book(db, book_id, **updates)
    if not b:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return _resp(b)


@router.patch("/{book_id}/price", response_model=BookResponse)
def update_book_price(
    book_id: int,
    payload: PriceUpdateRequest,
    db: Session = Depends(get_db),
):
    b = update_book(db, book_id, price=int(round(payload.price)))
    if not b:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return _resp(b)


@router.delete("/{book_id}", status_code=204)
def delete_one(book_id: int, db: Session = Depends(get_db)):
    if not delete_book(db, book_id):
        raise HTTPException(status_code=404, detail="Libro no encontrado")


@router.post("/{book_id}/publish", response_model=BookResponse)
def publish(book_id: int, db: Session = Depends(get_db)):
    try:
        b = publish_book(db, book_id)
        if not b:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        return _resp(b)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.patch("/{book_id}/mark-enriched", response_model=BookResponse)
def mark_enriched_endpoint(book_id: int, db: Session = Depends(get_db)):
    b = mark_enriched(db, book_id)
    if not b:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return _resp(b)