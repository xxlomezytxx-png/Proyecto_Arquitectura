from dataclasses import dataclass
from typing import Optional, List
import hashlib

_PUBLISHERS = [
    "Penguin Random House",
    "Editorial Planeta",
    "Alfaguara",
    "Anagrama",
    "Seix Barral",
    "Tusquets",
    "Destino",
    "Siruela"
]

_CATEGORIES = [
    "Ficción",
    "No Ficción",
    "Ciencia",
    "Historia",
    "Filosofía",
    "Tecnología",
    "Arte",
    "Economía"
]


@dataclass
class EnrichmentRequest:
    book_reference: str
    title: str
    author: str
    isbn: Optional[str] = None
    issn: Optional[str] = None


@dataclass
class EnrichmentResult:
    book_reference: str
    normalized_title: str
    normalized_author: str
    normalized_publisher: str
    description: str
    category: str
    keywords: List[str]
    cover_url: str
    publication_year: int
    source_used: str
    confidence_score: float
    metadata: dict


def _build_keywords(title: str, author: str, category: str) -> List[str]:
    base_keywords = {
        "Ficción": ["novela", "literatura", "narrativa"],
        "No Ficción": ["ensayo", "conocimiento", "análisis"],
        "Ciencia": ["investigación", "ciencia", "aprendizaje"],
        "Historia": ["historia", "contexto", "sociedad"],
        "Filosofía": ["pensamiento", "filosofía", "reflexión"],
        "Tecnología": ["tecnología", "innovación", "software"],
        "Arte": ["arte", "cultura", "creatividad"],
        "Economía": ["economía", "mercado", "finanzas"],
    }

    keywords = base_keywords.get(category, ["libros", "lectura", "bibliografía"]).copy()

    first_title_word = title.strip().split()[0].lower() if title.strip() else "libro"
    first_author_word = author.strip().split()[0].lower() if author.strip() else "autor"

    keywords.append(first_title_word)
    keywords.append(first_author_word)

    # quitar duplicados conservando orden
    seen = set()
    result = []
    for keyword in keywords:
        normalized = keyword.strip().lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(keyword)
    return result


def build_mock_result(req: EnrichmentRequest) -> EnrichmentResult:
    seed = int(hashlib.md5(req.book_reference.encode()).hexdigest()[:8], 16)

    publisher = _PUBLISHERS[seed % len(_PUBLISHERS)]
    category = _CATEGORIES[seed % len(_CATEGORIES)]
    year = 1980 + (seed % 44)
    score = round(0.65 + (seed % 35) / 100, 2)
    title_slug = req.title[:15].replace(" ", "+")
    keywords = _build_keywords(req.title, req.author, category)

    description = (
        f"Descripción enriquecida de '{req.title.strip()}' por {req.author.strip()}. "
        f"Publicado por {publisher} en {year}. "
        f"Clasificado de forma mock en la categoría {category} para Sprint 1."
    )

    return EnrichmentResult(
        book_reference=req.book_reference.strip(),
        normalized_title=req.title.strip().title(),
        normalized_author=req.author.strip().title(),
        normalized_publisher=publisher,
        description=description,
        category=category,
        keywords=keywords,
        cover_url=f"https://via.placeholder.com/200x300/4A90E2/FFFFFF?text={title_slug}",
        publication_year=year,
        source_used="mock_google_books",
        confidence_score=score,
        metadata={
            "isbn_verified": bool(req.isbn),
            "sources_consulted": ["mock_google_books", "mock_open_library"],
            "sprint": "1 - mock data",
            "ready_for_real_ai": True
        },
    )