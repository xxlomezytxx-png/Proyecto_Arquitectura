from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application import cart_use_cases
from app.dependencies import get_catalog_client
from app.infrastructure.clients.catalog_client import HttpCatalogClient
from app.infrastructure.clients.errors import UpstreamServiceError
from app.infrastructure.database.connection import get_db

router = APIRouter()


class AddItemRequest(BaseModel):
    book_id: str
    book_title: str
    quantity: int = 1
    unit_price: float = 0.0


class CartItemResponse(BaseModel):
    id: Optional[int]
    book_id: str
    book_title: str
    quantity: int
    unit_price: float


class CartResponse(BaseModel):
    id: Optional[int]
    customer_id: str
    status: str
    items: List[CartItemResponse]


def _item_resp(item) -> CartItemResponse:
    return CartItemResponse(
        id=item.id,
        book_id=item.book_id,
        book_title=item.book_title,
        quantity=item.quantity,
        unit_price=item.unit_price,
    )


def _cart_resp(cart) -> CartResponse:
    return CartResponse(
        id=cart.id,
        customer_id=cart.customer_id,
        status=cart.status.value,
        items=[_item_resp(i) for i in cart.items],
    )


@router.get("/{customer_id}", response_model=CartResponse)
def get_cart(customer_id: str, db: Session = Depends(get_db)):
    return _cart_resp(cart_use_cases.get_or_create_cart(db, customer_id))


@router.post("/{customer_id}/items", response_model=CartResponse, status_code=201)
async def add_item(
    customer_id: str,
    req: AddItemRequest,
    db: Session = Depends(get_db),
    catalog: HttpCatalogClient = Depends(get_catalog_client),
):
    if req.quantity < 1:
        raise HTTPException(status_code=422, detail="quantity must be >= 1")
    try:
        book = await catalog.get_book(req.book_id)
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book {req.book_id} not found in catalog")
    cart = cart_use_cases.add_item(
        db, customer_id, req.book_id, req.book_title, req.quantity, req.unit_price,
    )
    return _cart_resp(cart)


@router.delete("/{customer_id}/items/{book_id}", response_model=CartResponse)
def remove_item(customer_id: str, book_id: str, db: Session = Depends(get_db)):
    return _cart_resp(cart_use_cases.remove_item(db, customer_id, book_id))


@router.delete("/{customer_id}", status_code=204)
def clear_cart(customer_id: str, db: Session = Depends(get_db)):
    cart_use_cases.clear_cart(db, customer_id)
