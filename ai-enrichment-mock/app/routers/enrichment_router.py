from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from app.application.enrichment_use_cases import enrich_single, enrich_batch
from app.domain.enrichment import EnrichmentRequest

router = APIRouter()


class EnrichRequestBody(BaseModel):
    book_reference: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=2, max_length=200)
    author: str = Field(..., min_length=2, max_length=150)
    isbn: Optional[str] = Field(default=None, max_length=20)
    issn: Optional[str] = Field(default=None, max_length=20)

    @field_validator("book_reference")
    @classmethod
    def validate_book_reference(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("book_reference no puede estar vacío")
        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title no puede estar vacío")
        return value

    @field_validator("author")
    @classmethod
    def validate_author(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("author no puede estar vacío")
        return value

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        value = value.strip()
        if value == "":
            return None

        cleaned = value.replace("-", "").replace(" ", "")
        if not cleaned.isdigit():
            raise ValueError("isbn debe contener solo números, espacios o guiones")

        if len(cleaned) not in (10, 13):
            raise ValueError("isbn debe tener 10 o 13 dígitos")

        return value

    @field_validator("issn")
    @classmethod
    def validate_issn(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        value = value.strip()
        if value == "":
            return None

        cleaned = value.replace("-", "").replace(" ", "")
        if not cleaned.isdigit():
            raise ValueError("issn debe contener solo números, espacios o guiones")

        if len(cleaned) != 8:
            raise ValueError("issn debe tener 8 dígitos")

        return value


class EnrichBatchBody(BaseModel):
    items: List[EnrichRequestBody] = Field(..., min_length=1)


@router.post("/enrich")
def enrich_book(body: EnrichRequestBody):
    req = EnrichmentRequest(
        book_reference=body.book_reference,
        title=body.title,
        author=body.author,
        isbn=body.isbn,
        issn=body.issn,
    )
    result = enrich_single(req)
    return result.__dict__


@router.post("/enrich/batch")
def enrich_books_batch(body: EnrichBatchBody):
    requests = [
        EnrichmentRequest(
            book_reference=item.book_reference,
            title=item.title,
            author=item.author,
            isbn=item.isbn,
            issn=item.issn,
        )
        for item in body.items
    ]
    results = enrich_batch(requests)
    return [r.__dict__ for r in results]


@router.get("/health")
def health():
    return {"status": "ok", "service": "ai-enrichment-mock"}