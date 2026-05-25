from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.cart import Cart, CartItem, CartStatus
from app.infrastructure.database.models import CartItemModel, CartModel


def _cart_from_model(m: CartModel) -> Cart:
    items = [
        CartItem(
            id=ci.id,
            cart_id=ci.cart_id,
            book_id=ci.book_id,
            book_title=ci.book_title,
            quantity=ci.quantity,
            unit_price=ci.unit_price,
        )
        for ci in (m.items or [])
    ]
    return Cart(id=m.id, customer_id=m.customer_id, status=CartStatus(m.status), items=items)


def get_or_create_cart(db: Session, customer_id: str) -> Cart:
    m = db.query(CartModel).filter(
        CartModel.customer_id == customer_id,
        CartModel.status == CartStatus.OPEN,
    ).first()
    if not m:
        m = CartModel(customer_id=customer_id, status=CartStatus.OPEN)
        db.add(m)
        try:
            db.commit()
            db.refresh(m)
        except Exception:
            db.rollback()
            raise
    return _cart_from_model(m)


def add_item(
    db: Session,
    customer_id: str,
    book_id: str,
    book_title: str,
    quantity: int,
    unit_price: float,
) -> Cart:
    cart = get_or_create_cart(db, customer_id)
    m = db.query(CartModel).filter(CartModel.id == cart.id).first()
    existing = next((ci for ci in m.items if ci.book_id == book_id), None)
    if existing:
        existing.quantity += quantity
    else:
        db.add(CartItemModel(
            cart_id=m.id,
            book_id=book_id,
            book_title=book_title,
            quantity=quantity,
            unit_price=unit_price,
        ))
    try:
        db.commit()
        db.refresh(m)
    except Exception:
        db.rollback()
        raise
    return _cart_from_model(m)


def remove_item(db: Session, customer_id: str, book_id: str) -> Cart:
    cart = get_or_create_cart(db, customer_id)
    m = db.query(CartModel).filter(CartModel.id == cart.id).first()
    item = next((ci for ci in m.items if ci.book_id == book_id), None)
    if item:
        db.delete(item)
        try:
            db.commit()
            db.refresh(m)
        except Exception:
            db.rollback()
            raise
    return _cart_from_model(m)


def clear_cart(db: Session, customer_id: str) -> None:
    cart = get_or_create_cart(db, customer_id)
    m = db.query(CartModel).filter(CartModel.id == cart.id).first()
    for item in list(m.items):
        db.delete(item)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
