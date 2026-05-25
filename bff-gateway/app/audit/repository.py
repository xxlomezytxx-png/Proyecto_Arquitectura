import json
import logging
import uuid
from datetime import datetime, timezone

from app.audit.connection import SessionLocal
from app.audit.models import AuditEntry

logger = logging.getLogger(__name__)


def save_audit_entry(
    entity_type: str,
    entity_id: str,
    action: str,
    service_name: str,
    input_data: dict | None = None,
    output_data: dict | None = None,
) -> None:
    db = SessionLocal()
    try:
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            service_name=service_name,
            input_data=json.dumps(input_data) if input_data else None,
            output_data=json.dumps(output_data) if output_data else None,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(entry)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("audit save failed: %s", exc)
    finally:
        db.close()


def list_audit_entries(entity_type: str | None = None, limit: int = 50) -> list[dict]:
    db = SessionLocal()
    try:
        q = db.query(AuditEntry).order_by(AuditEntry.timestamp.desc())
        if entity_type:
            q = q.filter(AuditEntry.entity_type == entity_type)
        records = q.limit(limit).all()
        return [_to_dict(r) for r in records]
    except Exception as exc:
        logger.warning("audit list failed: %s", exc)
        return []
    finally:
        db.close()


def get_audit_entry(entry_id: str) -> dict | None:
    db = SessionLocal()
    try:
        record = db.query(AuditEntry).filter(AuditEntry.id == entry_id).first()
        return _to_dict(record) if record else None
    except Exception as exc:
        logger.warning("audit get failed: %s", exc)
        return None
    finally:
        db.close()


def get_audit_stats() -> dict:
    db = SessionLocal()
    try:
        total = db.query(AuditEntry).count()
        pricing_count = (
            db.query(AuditEntry)
            .filter(AuditEntry.entity_type == "pricing")
            .count()
        )
        order_count = (
            db.query(AuditEntry)
            .filter(AuditEntry.entity_type == "order")
            .count()
        )
        enrichment_count = (
            db.query(AuditEntry)
            .filter(AuditEntry.entity_type == "enrichment")
            .count()
        )
        return {
            "total": total,
            "pricing": pricing_count,
            "orders": order_count,
            "enrichment": enrichment_count,
        }
    except Exception as exc:
        logger.warning("audit stats failed: %s", exc)
        return {"total": 0, "pricing": 0, "orders": 0, "enrichment": 0}
    finally:
        db.close()


def get_audit_anomalies(limit: int = 50) -> list[dict]:
    """Return pricing decisions where suggested_price > 3x the average for that entity_id."""
    db = SessionLocal()
    try:
        records = (
            db.query(AuditEntry)
            .filter(AuditEntry.entity_type == "pricing")
            .order_by(AuditEntry.timestamp.desc())
            .limit(500)
            .all()
        )
        prices_by_book: dict[str, list[float]] = {}
        for r in records:
            try:
                out = json.loads(r.output_data) if r.output_data else {}
                price = float(out.get("suggested_price", 0))
                if price > 0:
                    prices_by_book.setdefault(r.entity_id, []).append(price)
            except (ValueError, TypeError):
                continue

        anomalies = []
        for r in records:
            try:
                out = json.loads(r.output_data) if r.output_data else {}
                price = float(out.get("suggested_price", 0))
                book_prices = prices_by_book.get(r.entity_id, [])
                if len(book_prices) < 2 or price <= 0:
                    continue
                avg = sum(book_prices) / len(book_prices)
                if avg > 0 and price > avg * 3:
                    entry = _to_dict(r)
                    entry["anomaly_reason"] = (
                        f"suggested_price {price:.2f} > 3x average {avg:.2f}"
                    )
                    anomalies.append(entry)
            except (ValueError, TypeError):
                continue

        return anomalies[:limit]
    except Exception as exc:
        logger.warning("audit anomalies failed: %s", exc)
        return []
    finally:
        db.close()


def _to_dict(record: AuditEntry) -> dict:
    return {
        "id": record.id,
        "entity_type": record.entity_type,
        "entity_id": record.entity_id,
        "action": record.action,
        "service_name": record.service_name,
        "input_data": json.loads(record.input_data) if record.input_data else None,
        "output_data": json.loads(record.output_data) if record.output_data else None,
        "timestamp": record.timestamp.isoformat(),
    }
