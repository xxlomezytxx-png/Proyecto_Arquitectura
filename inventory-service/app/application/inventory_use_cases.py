import io
import math
import re
import unicodedata

import pandas as pd
from sqlalchemy.orm import Session

from app.domain.inventory_item import (
    ImportBatch, ImportError, InventoryItem, ItemCondition,
)
from app.infrastructure import inventory_repository

REQUIRED_COLUMNS = {"title", "book_reference", "quantity_available"}


def _normalize_header(value: str) -> str:
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


_COLUMN_ALIASES = {
    "titulo_del_libro": "title",
    "isbn_13": "book_reference",
    "isbn_10": "external_code",
    "issn": "external_code",
    "estado_del_libro": "condition",
    "caracteristicas": "defects",
    "comentarios_opcionales": "observations",
    "unidades_disponibles": "quantity_available",
    "ubicacion_fisica_en_bodega_no_publicar_este_campo_en_luma": "location",
    "ubicacion_fisica_en_bodega": "location",
    "url_portada": "cover_url",
    "title": "title",
    "author": "author",
    "book_reference": "book_reference",
    "quantity_available": "quantity_available",
    "isbn": "isbn",
    "condition": "condition",
    "defects": "defects",
    "observations": "observations",
    "external_code": "external_code",
}


_CONDITION_ALIASES = {
    "nuevo": ItemCondition.NEW,
    "nueva": ItemCondition.NEW,
    "new": ItemCondition.NEW,
    "como nuevo": ItemCondition.LIKE_NEW,
    "like_new": ItemCondition.LIKE_NEW,
    "buen estado": ItemCondition.GOOD,
    "bueno": ItemCondition.GOOD,
    "good": ItemCondition.GOOD,
    "aceptable": ItemCondition.ACCEPTABLE,
    "acceptable": ItemCondition.ACCEPTABLE,
    "deteriorado": ItemCondition.POOR,
    "poor": ItemCondition.POOR,
    "muestra": ItemCondition.ACCEPTABLE,
}


def _clean_cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null", "nat"}:
        return ""
    return text


def _clean_numeric_identifier(value) -> str:
    text = _clean_cell(value)
    if not text:
        return ""
    if re.fullmatch(r"\d+\.0", text):
        text = text[:-2]
    return re.sub(r"[^0-9Xx]", "", text)


def _parse_quantity(value) -> int:
    try:
        text = _clean_cell(value)
        if not text:
            return 0
        return int(float(text))
    except Exception:
        return -1


def _parse_condition(value) -> ItemCondition:
    raw = _clean_cell(value).lower()
    raw = raw.replace("-", " ").replace("_", " ")
    raw = re.sub(r"\s+", " ", raw).strip()

    for key, condition in _CONDITION_ALIASES.items():
        if key in raw:
            return condition
    return ItemCondition.GOOD


def _read_dataframe(content: bytes, extension: str) -> pd.DataFrame:
    if extension in ("xlsx", "xls"):
        return pd.read_excel(io.BytesIO(content))

    if extension == "csv":
        for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
            try:
                return pd.read_csv(io.StringIO(content.decode(enc)))
            except UnicodeDecodeError:
                continue
        return pd.read_csv(io.StringIO(content.decode("utf-8", errors="replace")))

    raise ValueError(f"Formato no soportado: {extension}")


def process_inventory_file(db: Session, file_name: str, content: bytes, extension: str) -> ImportBatch:
    batch = inventory_repository.create_batch(db, file_name)

    try:
        df = _read_dataframe(content, extension)
    except Exception:
        inventory_repository.update_batch(db, batch.id, 0, 0, 0, "failed")
        raise

    df.columns = [_normalize_header(c) for c in df.columns]
    df.rename(columns={c: _COLUMN_ALIASES.get(c, c) for c in df.columns}, inplace=True)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        inventory_repository.update_batch(db, batch.id, 0, 0, 0, "failed")
        raise ValueError(f"Columnas requeridas faltantes: {missing}")

    processed = valid = invalid = 0

    for idx, row in df.iterrows():
        row_num = idx + 2
        processed += 1
        raw = str(row.to_dict())

        qty = _parse_quantity(row.get("quantity_available", 0))
        condition = _parse_condition(row.get("condition", "good"))

        book_ref = _clean_numeric_identifier(row.get("book_reference", ""))
        external_code = _clean_numeric_identifier(row.get("external_code", ""))
        isbn = _clean_numeric_identifier(row.get("isbn", "")) or book_ref or external_code

        if not book_ref:
            book_ref = external_code or isbn

        item = InventoryItem(
            id=None,
            external_code=external_code or None,
            book_reference=book_ref,
            title=_clean_cell(row.get("title", "")),
            isbn=isbn or None,
            quantity_available=qty,
            quantity_reserved=0,
            condition=condition,
            author=_clean_cell(row.get("author", "")),
            defects=[],
            observations=_clean_cell(row.get("observations", "")) or None,
            import_batch_id=batch.id,
            created_at=None,
        )

        errors = item.validate()

        if errors:
            invalid += 1
            for msg in errors:
                inventory_repository.create_error(
                    db,
                    ImportError(
                        id=None,
                        batch_id=batch.id,
                        row_number=row_num,
                        error_type="validation_error",
                        message=msg,
                        raw_data=raw,
                    ),
                )
        else:
            inventory_repository.create_item(db, item)
            valid += 1

    status = "completed" if valid > 0 else "failed"
    return inventory_repository.update_batch(db, batch.id, processed, valid, invalid, status)


def get_all_items(db: Session, skip: int = 0, limit: int = 100):
    return inventory_repository.get_all_items(db, skip, limit)


def get_item(db: Session, item_id: int):
    return inventory_repository.get_item_by_id(db, item_id)


def get_all_batches(db: Session):
    return inventory_repository.get_all_batches(db)


def get_batch(db: Session, batch_id: int):
    return inventory_repository.get_batch_by_id(db, batch_id)


def get_batch_errors(db: Session, batch_id: int):
    return inventory_repository.get_errors_by_batch(db, batch_id)


def get_batch_items(db: Session, batch_id: int):
    return inventory_repository.get_items_by_batch(db, batch_id)

def check_availability(db: Session, item_id: int, quantity: int = 1):
    item = inventory_repository.get_item_by_id(db, item_id)

    if not item:
        return {
            "available": False,
            "message": "Item no encontrado"
        }

    available_quantity = item.quantity_available - item.quantity_reserved

    return {
        "available": available_quantity >= quantity,
        "available_quantity": available_quantity,
        "requested_quantity": quantity,
        "item_id": item.id
    }


def reserve_stock(db: Session, item_id: int, quantity: int = 1):
    item = inventory_repository.get_item_by_id(db, item_id)

    if not item:
        return False

    available_quantity = item.quantity_available - item.quantity_reserved

    if available_quantity < quantity:
        return False

    item.quantity_reserved += quantity
    db.commit()
    db.refresh(item)

    return True


def release_stock(db: Session, item_id: int, quantity: int = 1):
    item = inventory_repository.get_item_by_id(db, item_id)

    if not item:
        return False

    item.quantity_reserved = max(0, item.quantity_reserved - quantity)

    db.commit()
    db.refresh(item)

    return True