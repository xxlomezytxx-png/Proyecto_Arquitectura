from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.inventory_use_cases import (
    get_all_batches, get_batch, get_batch_errors, get_batch_items,
    process_inventory_file,
)
from app.infrastructure.database import get_db

router = APIRouter()

ALLOWED_EXT = {"csv", "xlsx", "xls"}


class BatchResponse(BaseModel):
    id: int
    file_name: str
    upload_date: Optional[datetime]
    processed_rows: int
    valid_rows: int
    invalid_rows: int
    status: str


class ErrorResponse(BaseModel):
    id: int
    batch_id: int
    row_number: int
    error_type: str
    message: str
    raw_data: Optional[str]


def _bresp(b) -> BatchResponse:
    return BatchResponse(
        id=b.id, file_name=b.file_name, upload_date=b.upload_date,
        processed_rows=b.processed_rows, valid_rows=b.valid_rows,
        invalid_rows=b.invalid_rows, status=b.status.value,
    )


@router.post("/upload", response_model=BatchResponse, status_code=201)
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"Solo se permiten: {ALLOWED_EXT}")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Archivo demasiado grande (máx 10 MB)")
    try:
        batch = process_inventory_file(db, file.filename, content, ext)
        return _bresp(batch)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/", response_model=List[BatchResponse])
def list_batches(db: Session = Depends(get_db)):
    return [_bresp(b) for b in get_all_batches(db)]


@router.get("/{batch_id}", response_model=BatchResponse)
def get_one(batch_id: int, db: Session = Depends(get_db)):
    b = get_batch(db, batch_id)
    if not b:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    return _bresp(b)


@router.get("/{batch_id}/errors", response_model=List[ErrorResponse])
def errors(batch_id: int, db: Session = Depends(get_db)):
    return [ErrorResponse(id=e.id, batch_id=e.batch_id, row_number=e.row_number,
                          error_type=e.error_type, message=e.message, raw_data=e.raw_data)
            for e in get_batch_errors(db, batch_id)]


@router.get("/{batch_id}/items")
def items(batch_id: int, db: Session = Depends(get_db)):
    return [{"id": i.id, "title": i.title, "author": i.author,
             "book_reference": i.book_reference, "quantity_available": i.quantity_available,
             "condition": i.condition.value}
            for i in get_batch_items(db, batch_id)]
