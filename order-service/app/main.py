from __future__ import annotations
import logging

from fastapi import FastAPI
from sqlalchemy import text

from app.infrastructure.database.connection import Base, engine, SessionLocal

logger = logging.getLogger(__name__)
from app.infrastructure.database.models import OrderItemModel, OrderModel, CartModel, CartItemModel  # noqa: F401  registers tables
from app.routers.order_router import router as order_router
from app.routers.cart_router import router as cart_router

Base.metadata.create_all(bind=engine)

if engine.dialect.name == "postgresql":
    with engine.connect() as _conn:
        column_rows = _conn.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='orders'"
        ))
        existing_columns = {row[0] for row in column_rows}

        required_columns = {
            "customer_id",
            "total_amount",
            "cancel_reason",
            "created_at",
            "confirmed_at",
            "cancelled_at",
            "fulfilled_at",
        }

        if not required_columns.issubset(existing_columns):
            logger.warning(
                "Order schema incompatible; recreating orders/order_items tables. existing_columns=%s",
                existing_columns,
            )
            _conn.execute(text("DROP TABLE IF EXISTS order_items CASCADE"))
            _conn.execute(text("DROP TABLE IF EXISTS orders CASCADE"))
            _conn.commit()
            Base.metadata.create_all(bind=engine)

        _conn.execute(text(
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS customer_id VARCHAR(100) NOT NULL DEFAULT ''"
        ))
        _conn.execute(text(
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS total_amount FLOAT NOT NULL DEFAULT 0.0"
        ))
        _conn.execute(text(
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS cancel_reason TEXT"
        ))
        _conn.execute(text(
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS confirmed_at TIMESTAMP"
        ))
        _conn.execute(text(
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMP"
        ))
        _conn.execute(text(
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS fulfilled_at TIMESTAMP"
        ))
        _conn.execute(text(
            "ALTER TABLE order_items ADD COLUMN IF NOT EXISTS book_reference VARCHAR(200)"
        ))
        _conn.execute(text(
            "ALTER TABLE order_items ADD COLUMN IF NOT EXISTS book_title VARCHAR(500)"
        ))
        _conn.execute(text(
            "ALTER TABLE order_items ADD COLUMN IF NOT EXISTS unit_price FLOAT NOT NULL DEFAULT 0.0"
        ))
        _conn.commit()

app = FastAPI(
    title="BookFlow Order Service",
    version="0.1.0",
    description="Sprint 3 — pedido formal con state machine y validación de stock",
)

app.include_router(order_router, prefix="/orders", tags=["orders"])
app.include_router(cart_router, prefix="/cart", tags=["cart"])


@app.get("/health")
def health() -> dict:
    db_status = "disconnected"
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        logger.warning("Health check DB probe failed: %s", exc)
    finally:
        db.close()
    return {"status": "ok", "service": "order-service", "version": "0.1.0", "db": db_status}
