import logging

import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.application.use_cases.enrich_book import EnrichBookUseCase
from app.config import CATALOG_SERVICE_URL
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.enrichment_repository import EnrichmentRepository
from app.infrastructure.adapters import (crossref_adapter, google_books_adapter,
                                          open_library_adapter)

router = APIRouter()
logger = logging.getLogger(__name__)


class EnrichRequest(BaseModel):
    book_id: str
    isbn: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None


def _push_enrichment_to_catalog(book_id_str: str, result: dict) -> None:
    try:
        book_id = int(book_id_str)
    except (TypeError, ValueError):
        logger.warning("Cannot push enrichment to catalog: book_id '%s' is not an integer", book_id_str)
        return

    update_payload: dict = {}
    if result.get("normalized_description"):
        update_payload["description"] = result["normalized_description"]
    if result.get("cover_url"):
        update_payload["cover_url"] = result["cover_url"]
    if result.get("normalized_publisher"):
        update_payload["publisher"] = result["normalized_publisher"]
    if result.get("normalized_title"):
        update_payload["title"] = result["normalized_title"]
    if result.get("normalized_author"):
        update_payload["author"] = result["normalized_author"]

    if update_payload:
        try:
            resp = requests.put(
                f"{CATALOG_SERVICE_URL}/products/{book_id}",
                json=update_payload,
                timeout=5,
            )
            if not resp.ok:
                logger.warning("Catalog PUT /products/%d returned %d: %s", book_id, resp.status_code, resp.text[:200])
        except requests.RequestException as exc:
            logger.warning("Failed to update catalog book %d: %s", book_id, exc)

    try:
        resp = requests.patch(
            f"{CATALOG_SERVICE_URL}/products/{book_id}/mark-enriched",
            timeout=5,
        )
        if not resp.ok:
            logger.warning("Catalog PATCH mark-enriched for book %d returned %d", book_id, resp.status_code)
    except requests.RequestException as exc:
        logger.warning("Failed to mark catalog book %d as enriched: %s", book_id, exc)


@router.post("/enrich")
async def enrich_book(payload: EnrichRequest, db: Session = Depends(get_db)):
    if not payload.isbn and not payload.title:
        raise HTTPException(status_code=422, detail="isbn or title is required")

    repo = EnrichmentRepository(db)
    use_case = EnrichBookUseCase(repo)
    result = await use_case.execute(
        book_id=payload.book_id,
        isbn=payload.isbn,
        title=payload.title,
        author=payload.author,
        publisher=payload.publisher,
    )

    if result.get("status") == "completed":
        _push_enrichment_to_catalog(payload.book_id, result)

    return result


@router.get("/enrich/{request_id}")
def get_enrichment(request_id: int, db: Session = Depends(get_db)):
    repo = EnrichmentRepository(db)
    req = repo.get_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Enrichment request not found")
    result = repo.get_result_by_request(request_id)
    return {
        "request_id": req.id,
        "status": req.status,
        "source_used": req.source_used,
        "normalized_title": result.normalized_title if result else None,
        "normalized_author": result.normalized_author if result else None,
        "cover_url": result.cover_url if result else None,
        "confidence_score": result.confidence_score if result else 0.0,
    }


@router.get("/external-apis/status")
def external_apis_status():
    return {
        "apis": [
            google_books_adapter.get_status(),
            open_library_adapter.get_status(),
            crossref_adapter.get_status(),
        ]
    }
