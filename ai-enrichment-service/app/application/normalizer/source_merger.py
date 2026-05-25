"""Merge BookMetadata results from multiple sources, preferring higher confidence."""
from typing import Optional

from app.application.normalizer.author_formatter import format_author
from app.application.normalizer.text_normalizer import normalize_publisher, normalize_title
from app.application.normalizer.isbn_validator import validate_and_normalize
from app.application.normalizer.duplicate_detector import remove_duplicates
from app.domain.entities.enrichment import BookMetadata


def merge_results(results: list[BookMetadata]) -> Optional[BookMetadata]:
    if not results:
        return None

    # 🔥 Eliminar duplicados antes de procesar
    unique_results = remove_duplicates(results)

    # Ordenar por confianza
    sorted_results = sorted(unique_results, key=lambda r: r.confidence_score, reverse=True)

    def first_non_none(attr: str):
        return next((getattr(r, attr) for r in sorted_results if getattr(r, attr)), None)

    best = sorted_results[0]

    return BookMetadata(
        title=normalize_title(first_non_none("title")),
        author=format_author(first_non_none("author")),
        publisher=normalize_publisher(first_non_none("publisher")),
        description=first_non_none("description"),
        cover_url=first_non_none("cover_url"),
        isbn=validate_and_normalize(first_non_none("isbn")),  # 🔥 normaliza ISBN
        publication_year=first_non_none("publication_year"),
        source=best.source,
        confidence_score=best.confidence_score,
    )