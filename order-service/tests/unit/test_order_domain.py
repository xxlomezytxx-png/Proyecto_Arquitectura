from __future__ import annotations

from datetime import datetime

import pytest

from app.domain.entities.order import (IllegalStateTransitionError, Order,
                                       OrderItem, OrderStatus, can_transition)


pytestmark = pytest.mark.unit


def _make_order(status: OrderStatus = OrderStatus.PENDING) -> Order:
    return Order(
        customer_id="cust-1",
        items=(OrderItem(book_id="b1", book_title="t1", quantity=2, unit_price=10.0),),
        status=status,
    )


class TestOrderItem:
    def test_line_total_calculated_from_quantity_and_unit_price(self) -> None:
        item = OrderItem(book_id="b1", book_title="t1", quantity=3, unit_price=4.5)
        assert item.line_total == 13.5

    def test_quantity_must_be_positive(self) -> None:
        with pytest.raises(ValueError):
            OrderItem(book_id="b1", book_title="t1", quantity=0, unit_price=10.0)

    def test_unit_price_must_be_non_negative(self) -> None:
        with pytest.raises(ValueError):
            OrderItem(book_id="b1", book_title="t1", quantity=1, unit_price=-1.0)


class TestOrderTotal:
    def test_total_amount_sums_line_totals(self) -> None:
        order = Order(
            customer_id="cust-1",
            items=(
                OrderItem("b1", "t1", quantity=2, unit_price=10.0),
                OrderItem("b2", "t2", quantity=1, unit_price=5.5),
            ),
        )
        assert order.total_amount == 25.5

    def test_order_must_have_items(self) -> None:
        with pytest.raises(ValueError):
            Order(customer_id="c", items=())

    def test_order_requires_customer_id(self) -> None:
        with pytest.raises(ValueError):
            Order(
                customer_id="",
                items=(OrderItem("b", "t", 1, 1.0),),
            )


class TestStateMachine:
    @pytest.mark.parametrize(
        "current, target, allowed",
        [
            (OrderStatus.PENDING, OrderStatus.CONFIRMED, True),
            (OrderStatus.PENDING, OrderStatus.CANCELLED, True),
            (OrderStatus.PENDING, OrderStatus.FULFILLED, False),
            (OrderStatus.CONFIRMED, OrderStatus.FULFILLED, True),
            (OrderStatus.CONFIRMED, OrderStatus.CANCELLED, True),
            (OrderStatus.CONFIRMED, OrderStatus.PENDING, False),
            (OrderStatus.CANCELLED, OrderStatus.PENDING, False),
            (OrderStatus.CANCELLED, OrderStatus.CONFIRMED, False),
            (OrderStatus.FULFILLED, OrderStatus.CANCELLED, False),
            (OrderStatus.FULFILLED, OrderStatus.PENDING, False),
        ],
    )
    def test_can_transition_matrix(
        self,
        current: OrderStatus,
        target: OrderStatus,
        allowed: bool,
    ) -> None:
        assert can_transition(current, target) is allowed

    def test_transition_to_confirmed_sets_timestamp(self) -> None:
        order = _make_order()
        confirmed = order.transition_to(OrderStatus.CONFIRMED)
        assert confirmed.status is OrderStatus.CONFIRMED
        assert isinstance(confirmed.confirmed_at, datetime)

    def test_transition_to_cancelled_records_reason(self) -> None:
        order = _make_order()
        cancelled = order.transition_to(OrderStatus.CANCELLED, reason="customer changed mind")
        assert cancelled.status is OrderStatus.CANCELLED
        assert cancelled.cancel_reason == "customer changed mind"
        assert cancelled.cancelled_at is not None

    def test_transition_returns_new_instance_does_not_mutate_original(self) -> None:
        order = _make_order()
        confirmed = order.transition_to(OrderStatus.CONFIRMED)
        assert order.status is OrderStatus.PENDING
        assert order is not confirmed

    def test_illegal_transition_raises(self) -> None:
        order = _make_order(status=OrderStatus.FULFILLED)
        with pytest.raises(IllegalStateTransitionError):
            order.transition_to(OrderStatus.CONFIRMED)

    def test_pending_to_fulfilled_blocked(self) -> None:
        order = _make_order()
        with pytest.raises(IllegalStateTransitionError):
            order.transition_to(OrderStatus.FULFILLED)

    def test_full_lifecycle_pending_to_fulfilled(self) -> None:
        order = _make_order()
        confirmed = order.transition_to(OrderStatus.CONFIRMED)
        fulfilled = confirmed.transition_to(OrderStatus.FULFILLED)
        assert fulfilled.status is OrderStatus.FULFILLED
        assert fulfilled.confirmed_at is not None
        assert fulfilled.fulfilled_at is not None
