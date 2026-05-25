from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.application.dtos import CreateOrderInput, OrderItemInput
from app.application.errors import (InsufficientStockError, OrderNotFoundError)
from app.application.use_cases.cancel_order import CancelOrderUseCase
from app.application.use_cases.confirm_order import ConfirmOrderUseCase
from app.application.use_cases.create_order import (BookNotFoundError,
                                                    CreateOrderUseCase,
                                                    MissingPriceError)
from app.application.use_cases.fulfill_order import FulfillOrderUseCase
from app.dependencies import (get_cancel_order_use_case,
                              get_confirm_order_use_case,
                              get_create_order_use_case,
                              get_fulfill_order_use_case,
                              get_order_repository)
from app.domain.entities.order import IllegalStateTransitionError, Order
from app.infrastructure.clients.errors import UpstreamServiceError
from app.infrastructure.database.repositories.order_repository import \
    SqlAlchemyOrderRepository

router = APIRouter()


class OrderItemRequest(BaseModel):
    book_id: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price_override: Optional[float] = Field(default=None, ge=0)


class CreateOrderRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    items: list[OrderItemRequest] = Field(min_length=1)


class CancelOrderRequest(BaseModel):
    reason: Optional[str] = None


class OrderItemResponse(BaseModel):
    book_id: str
    book_title: str
    quantity: int
    unit_price: float
    line_total: float


class OrderResponse(BaseModel):
    id: int
    customer_id: str
    status: str
    items: list[OrderItemResponse]
    total_amount: float
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    fulfilled_at: Optional[datetime] = None
    cancel_reason: Optional[str] = None


def _to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id or 0,
        customer_id=order.customer_id,
        status=order.status.value,
        items=[
            OrderItemResponse(
                book_id=item.book_id,
                book_title=item.book_title,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=item.line_total,
            )
            for item in order.items
        ],
        total_amount=order.total_amount,
        created_at=order.created_at,
        confirmed_at=order.confirmed_at,
        cancelled_at=order.cancelled_at,
        fulfilled_at=order.fulfilled_at,
        cancel_reason=order.cancel_reason,
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: CreateOrderRequest,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
) -> OrderResponse:
    try:
        order = await use_case.execute(
            CreateOrderInput(
                customer_id=payload.customer_id,
                items=tuple(
                    OrderItemInput(
                        book_id=i.book_id,
                        quantity=i.quantity,
                        unit_price_override=i.unit_price_override,
                    )
                    for i in payload.items
                ),
            )
        )
    except BookNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MissingPriceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return _to_response(order)


@router.post("/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(
    order_id: int,
    use_case: ConfirmOrderUseCase = Depends(get_confirm_order_use_case),
) -> OrderResponse:
    try:
        order = await use_case.execute(order_id)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except IllegalStateTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InsufficientStockError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "insufficient_stock",
                "shortages": [
                    {
                        "book_id": s.book_id,
                        "requested": s.requested,
                        "available": s.available,
                    }
                    for s in exc.shortages
                ],
            },
        ) from exc
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return _to_response(order)


@router.post("/{order_id}/fulfill", response_model=OrderResponse)
def fulfill_order(
    order_id: int,
    use_case: FulfillOrderUseCase = Depends(get_fulfill_order_use_case),
) -> OrderResponse:
    try:
        order = use_case.execute(order_id)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except IllegalStateTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _to_response(order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    payload: CancelOrderRequest,
    use_case: CancelOrderUseCase = Depends(get_cancel_order_use_case),
) -> OrderResponse:
    try:
        order = use_case.execute(order_id, reason=payload.reason)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except IllegalStateTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _to_response(order)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    repo: SqlAlchemyOrderRepository = Depends(get_order_repository),
) -> OrderResponse:
    order = repo.get_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"order {order_id} not found")
    return _to_response(order)


@router.get("", response_model=list[OrderResponse])
def list_orders(
    customer_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    repo: SqlAlchemyOrderRepository = Depends(get_order_repository),
) -> list[OrderResponse]:
    if customer_id:
        orders = repo.list_by_customer(customer_id, limit=limit, offset=offset)
    else:
        orders = repo.list_all(limit=limit, offset=offset)
    return [_to_response(o) for o in orders]
