from typing import List
from app.domain.entities.enrichment import BookMetadata
from app.application.normalizer.isbn_validator import validate_and_normalize
from app.application.normalizer.text_normalizer import normalize_title


def remove_duplicates(results: List[BookMetadata]) -> List[BookMetadata]:
    seen = set()
    unique = []

    for r in results:
        # 🔥 Prioridad: ISBN
        isbn = validate_and_normalize(r.isbn) if r.isbn else None

        if isbn:
            key = f"isbn:{isbn}"
        else:
            # 🔥 fallback: título + autor
            title = normalize_title(r.title)
            author = (r.author or "").strip().lower()

            # Si no hay datos suficientes, lo dejamos pasar sin filtrar fuerte
            if not title and not author:
                key = f"unique:{id(r)}"
            else:
                key = f"title:{title}|author:{author}"

        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique