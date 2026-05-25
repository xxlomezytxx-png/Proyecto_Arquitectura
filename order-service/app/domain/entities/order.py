from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    FULFILLED = "FULFILLED"


_ALLOWED_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    OrderStatus.PENDING: frozenset({OrderStatus.CONFIRMED, OrderStatus.CANCELLED}),
    OrderStatus.CONFIRMED: frozenset({OrderStatus.FULFILLED, OrderStatus.CANCELLED}),
    OrderStatus.CANCELLED: frozenset(),
    OrderStatus.FULFILLED: frozenset(),
}


class IllegalStateTransitionError(ValueError):
    """Raised when an order status transition is not allowed."""


def can_transition(current: OrderStatus, target: OrderStatus) -> bool:
    return target in _ALLOWED_TRANSITIONS[current]


@dataclass(frozen=True)
class OrderItem:
    book_id: str
    book_title: str
    quantity: int
    unit_price: float
    book_reference: Optional[str] = None

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("OrderItem.quantity must be > 0")
        if self.unit_price < 0:
            raise ValueError("OrderItem.unit_price must be >= 0")

    @property
    def line_total(self) -> float:
        return round(self.quantity * self.unit_price, 2)


@dataclass(frozen=True)
class Order:
    customer_id: str
    items: tuple[OrderItem, ...]
    status: OrderStatus = OrderStatus.PENDING
    id: Optional[int] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    fulfilled_at: Optional[datetime] = None
    cancel_reason: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("Order must contain at least one item")
        if not self.customer_id:
            raise ValueError("Order.customer_id is required")

    @property
    def total_amount(self) -> float:
        return round(sum(item.line_total for item in self.items), 2)

    def transition_to(
        self,
        target: OrderStatus,
        *,
        now: Optional[datetime] = None,
        reason: Optional[str] = None,
    ) -> "Order":
        if not can_transition(self.status, target):
            raise IllegalStateTransitionError(
                f"Cannot transition order from {self.status.value} to {target.value}"
            )
        timestamp = now or datetime.now(timezone.utc)
        if target is OrderStatus.CONFIRMED:
            return replace(self, status=target, confirmed_at=timestamp)
        if target is OrderStatus.CANCELLED:
            return replace(
                self, status=target, cancelled_at=timestamp, cancel_reason=reason
            )
        if target is OrderStatus.FULFILLED:
            return replace(self, status=target, fulfilled_at=timestamp)
        return replace(self, status=target)
