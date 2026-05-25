from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.order import Order, OrderItem, OrderStatus
from app.domain.interfaces.order_repository import OrderRepository
from app.infrastructure.database.models import OrderItemModel, OrderModel


def _model_to_domain(model: OrderModel) -> Order:
    items = tuple(
        OrderItem(
            book_id=item.book_id,
            book_title=item.book_title,
            quantity=item.quantity,
            unit_price=float(item.unit_price),
            book_reference=item.book_reference,
        )
        for item in model.items
    )
    return Order(
        id=model.id,
        customer_id=model.customer_id,
        items=items,
        status=OrderStatus(model.status.value if hasattr(model.status, "value") else model.status),
        created_at=model.created_at,
        confirmed_at=model.confirmed_at,
        cancelled_at=model.cancelled_at,
        fulfilled_at=model.fulfilled_at,
        cancel_reason=model.cancel_reason,
    )


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, order: Order) -> Order:
        model = OrderModel(
            customer_id=order.customer_id,
            status=order.status,
            total_amount=order.total_amount,
            created_at=order.created_at,
        )
        for item in order.items:
            model.items.append(
                OrderItemModel(
                    book_id=item.book_id,
                    book_reference=item.book_reference,
                    book_title=item.book_title,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
            )
        self._db.add(model)
        try:
            self._db.commit()
            self._db.refresh(model)
        except Exception:
            self._db.rollback()
            raise
        return _model_to_domain(model)

    def get_by_id(self, order_id: int) -> Optional[Order]:
        model = self._db.query(OrderModel).filter(OrderModel.id == order_id).first()
        return _model_to_domain(model) if model else None

    def list_by_customer(
        self, customer_id: str, limit: int = 50, offset: int = 0
    ) -> list[Order]:
        models = (
            self._db.query(OrderModel)
            .filter(OrderModel.customer_id == customer_id)
            .order_by(OrderModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [_model_to_domain(m) for m in models]

    def list_all(self, limit: int = 50, offset: int = 0) -> list[Order]:
        models = (
            self._db.query(OrderModel)
            .order_by(OrderModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [_model_to_domain(m) for m in models]

    def update(self, order: Order) -> Order:
        if order.id is None:
            raise ValueError("Cannot update an order without an id")
        model = self._db.query(OrderModel).filter(OrderModel.id == order.id).first()
        if model is None:
            raise LookupError(f"order {order.id} not found")
        model.status = order.status
        model.total_amount = order.total_amount
        model.confirmed_at = order.confirmed_at
        model.cancelled_at = order.cancelled_at
        model.fulfilled_at = order.fulfilled_at
        model.cancel_reason = order.cancel_reason
        try:
            self._db.commit()
            self._db.refresh(model)
        except Exception:
            self._db.rollback()
            raise
        return _model_to_domain(model)
