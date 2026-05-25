from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.inventory_use_cases import (
    check_availability, get_all_items, get_item, reserve_stock,
)
from app.infrastructure.database import get_db

router = APIRouter()


class ReserveRequest(BaseModel):
    quantity: int


class ItemResponse(BaseModel):
    id: int
    external_code: Optional[str]
    book_reference: str
    title: str
    author: str
    isbn: Optional[str]
    quantity_available: int
    quantity_reserved: int
    condition: str
    defects: Optional[list]
    observations: Optional[str]
    import_batch_id: Optional[int]
    created_at: Optional[datetime]


def _resp(i) -> ItemResponse:
    serialized_defects = (
        [{"type": d.type.value, "description": d.description} for d in i.defects]
        if i.defects else None
    )
    return ItemResponse(
        id=i.id, external_code=i.external_code, book_reference=i.book_reference,
        title=i.title, author=i.author, isbn=i.isbn,
        quantity_available=i.quantity_available, quantity_reserved=i.quantity_reserved,
        condition=i.condition.value, defects=serialized_defects, observations=i.observations,
        import_batch_id=i.import_batch_id, created_at=i.created_at,
    )


@router.get("/health")
def health():
    return {"status": "ok", "service": "inventory-service"}


@router.get("/", response_model=List[ItemResponse])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return [_resp(i) for i in get_all_items(db, skip, limit)]


@router.get("/availability/{book_reference}")
def availability(book_reference: str, db: Session = Depends(get_db)):
    qty = check_availability(db, book_reference)
    return {"book_reference": book_reference, "quantity_available": qty, "is_available": qty > 0}


@router.patch("/availability/{book_reference}/reserve")
def reserve(book_reference: str, body: ReserveRequest, db: Session = Depends(get_db)):
    if body.quantity < 1:
        raise HTTPException(status_code=422, detail="quantity must be >= 1")
    ok = reserve_stock(db, book_reference, body.quantity)
    if not ok:
        raise HTTPException(status_code=409, detail="Insufficient stock")
    return {"book_reference": book_reference, "reserved": body.quantity}


@router.get("/{item_id}", response_model=ItemResponse)
def get_one(item_id: int, db: Session = Depends(get_db)):
    item = get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    return _resp(item)
