import re

import pandas as pd
import requests
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.config import CATALOG_SERVICE_URL, INVENTORY_SERVICE_URL
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import (
    EnrichmentRequestModel,
    EnrichmentResultModel,
    EnrichmentStatusDB,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def clean_value(value) -> str:
    if value is None:
        return ""
    value = str(value).strip()
    if value.lower() in ["nan", "none", "null"]:
        return ""
    return value


def clean_isbn(value) -> str:
    return re.sub(r"[^0-9Xx]", "", clean_value(value))


def clean_stock(value):
    try:
        if value is None or str(value).strip().lower() in ["", "nan", "none", "null"]:
            return None
        return int(float(value))
    except Exception:
        return None


def normalize_text(value: str) -> str:
    value = clean_value(value).lower()
    value = re.sub(r"[^a-záéíóúñ0-9 ]", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def generate_placeholder_cover(title: str) -> str:
    safe_title = (clean_value(title) or "Libro").replace(" ", "+")
    return f"https://placehold.co/300x450/2F6F52/FFFFFF?text={safe_title}&font=roboto"

def sync_excel_with_inventory(file_bytes: bytes, filename: str) -> dict:
    try:
        files = {
            "file": (
                filename,
                file_bytes,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }

        resp = requests.post(
            f"{INVENTORY_SERVICE_URL}/batches/upload",
            files=files,
            timeout=120,
        )

        if resp.status_code in [200, 201]:
            return {
                "status": "SYNCED",
                "inventory_batch": resp.json(),
            }

        return {
            "status": "FAILED",
            "status_code": resp.status_code,
            "response": resp.text,
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "message": str(exc),
        }
# ---------------------------------------------------------------------------
# Category mapping
# ---------------------------------------------------------------------------

def map_category_id(categories: list, title: str = "", description: str = "") -> int:
    text = " ".join(categories or []).lower()
    text += " " + normalize_text(title)
    text += " " + normalize_text(description or "")

    exact_map = {
        "clean code": 7,
        "atomic habits": 2,
        "rich dad poor dad": 10,
        "padre rico": 10,
        "padre pobre": 10,
        "sapiens": 4,
        "de animales a dioses": 4,
        "the road": 1,
        "pensar rapido": 2,
        "pensar rápido": 2,
        "thinking fast and slow": 2,
        "daniel kahneman": 2,
        "capitalismo de la vigilancia": 7,
    }
    for phrase, cat_id in exact_map.items():
        if phrase in text:
            return cat_id

    keyword_map = [
        (7, ["computer", "computers", "programming", "software", "technology",
             "data", "engineering", "code", "coding", "developer",
             "architecture", "python", "java", "javascript", "database",
             "algorithm", "systems", "digital", "artificial intelligence"]),
        (10, ["business", "economics", "finance", "money", "management",
              "investment", "financial", "negocios", "finanzas", "economía",
              "economia", "empresa", "mercado", "capitalism", "capitalismo"]),
        (4, ["history", "historical", "civilization", "anthropology",
             "humanity", "humanidad", "historia", "war", "guerra"]),
        (3, ["science", "physics", "biology", "chemistry", "mathematics",
             "cosmos", "universe", "astronomy", "energy", "solar",
             "photovoltaic", "fotovoltaica"]),
        (2, ["self-help", "psychology", "personal", "habits", "habit",
             "mind", "success", "health", "behavior", "productivity",
             "autoayuda", "psicología", "psicologia", "decisiones"]),
        (5, ["philosophy", "stoic", "ethics", "meditations", "sofía",
             "filosofía", "filosofia"]),
        (9, ["law", "legal", "derecho", "jurídico", "juridico"]),
        (8, ["children", "juvenile fiction", "kids", "infantil"]),
        (6, ["painting", "music", "drawing", "art history", "artes", "arte", "design"]),
        (1, ["fiction", "novel", "fantasy", "romance", "mystery",
             "thriller", "story", "stories", "literature", "novela"]),
    ]
    for cat_id, keywords in keyword_map:
        if any(word in text for word in keywords):
            return cat_id

    return 2


# ---------------------------------------------------------------------------
# External API calls (sync — compatible with pandas processing loop)
# ---------------------------------------------------------------------------

def _safe(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _google_cover(image_links: dict) -> str:
    if not image_links:
        return ""
    cover = (
        image_links.get("extraLarge")
        or image_links.get("large")
        or image_links.get("medium")
        or image_links.get("small")
        or image_links.get("thumbnail")
        or ""
    )
    return cover.replace("http://", "https://")


def google_books_sync(isbn: str = "", title: str = "", author: str = ""):
    queries = []
    if isbn:
        queries.append(f"isbn:{isbn}")
    if title:
        q = f'intitle:"{title}"'
        if author:
            q += f' inauthor:"{author}"'
        queries.append(q)

    for query in queries:
        try:
            resp = requests.get(
                "https://www.googleapis.com/books/v1/volumes",
                params={"q": query, "maxResults": 1},
                timeout=10,
            )
            if resp.status_code != 200:
                continue
            data = resp.json()
            if not data.get("items"):
                continue
            info = data["items"][0].get("volumeInfo", {})
            return {
                "source": "Google Books",
                "title": _safe(info.get("title")) or _safe(title),
                "author": ", ".join(info.get("authors", [])) or _safe(author) or "Autor no disponible",
                "publisher": _safe(info.get("publisher")) or None,
                "publication_year": _safe(info.get("publishedDate"))[:4] or None,
                "description": _safe(info.get("description")) or None,
                "cover": _google_cover(info.get("imageLinks", {})),
                "categories": info.get("categories", []),
                "confidence": "HIGH" if isbn else "MEDIUM",
            }
        except Exception:
            continue
    return None


def _resolve_ol_authors(author_keys: list) -> str:
    names = []
    for entry in author_keys[:3]:
        key = entry.get("key", "") if isinstance(entry, dict) else str(entry)
        if not key:
            continue
        try:
            resp = requests.get(f"https://openlibrary.org{key}.json", timeout=5)
            if resp.status_code == 200:
                name = _safe(resp.json().get("name", ""))
                if name:
                    names.append(name)
        except Exception:
            continue
    return "; ".join(names)


def open_library_sync(isbn: str = "", title: str = "", author: str = ""):
    if not isbn:
        return None
    try:
        resp = requests.get(
            f"https://openlibrary.org/isbn/{isbn}.json",
            timeout=10,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        covers = data.get("covers", [])
        if covers:
            cover = f"https://covers.openlibrary.org/b/id/{covers[0]}-L.jpg"
        else:
            cover = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"
        description = data.get("description")
        if isinstance(description, dict):
            description = description.get("value")
        resolved_author = (
            _resolve_ol_authors(data.get("authors", []))
            or _safe(author)
            or "Autor no disponible"
        )
        return {
            "source": "Open Library",
            "title": _safe(data.get("title")) or _safe(title),
            "author": resolved_author,
            "publisher": data.get("publishers", [None])[0] if data.get("publishers") else None,
            "publication_year": _safe(data.get("publish_date"))[-4:] if data.get("publish_date") else None,
            "description": _safe(description) or None,
            "cover": cover,
            "categories": data.get("subjects", []),
            "confidence": "MEDIUM",
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Catalog integration
# ---------------------------------------------------------------------------

def catalog_book_exists(isbn: str, title: str):
    try:
        resp = requests.get(
            f"{CATALOG_SERVICE_URL}/products/?limit=100000",
            timeout=15,
        )
        if resp.status_code != 200:
            return None
        books = resp.json()
        norm_isbn = clean_isbn(isbn)
        norm_title = normalize_text(title)
        for book in books:
            if norm_isbn and clean_isbn(book.get("isbn")) == norm_isbn:
                return book
            if norm_title and normalize_text(book.get("title", "")) == norm_title:
                return book
        return None
    except Exception:
        return None


def sync_with_catalog(result: dict, isbn: str) -> dict:
    title = clean_value(result.get("title")) or "Título no disponible"
    author = clean_value(result.get("author")) or "Autor no disponible"
    isbn = clean_isbn(isbn)

    existing = catalog_book_exists(isbn, title)
    if existing:
        return {"status": "ALREADY_EXISTS", "catalog_book": existing}

    try:
        cover = clean_value(result.get("cover")) or generate_placeholder_cover(title)
        category_id = map_category_id(
            result.get("categories", []),
            title=title,
            description=result.get("description") or "",
        )
        payload = {
            "title": title,
            "author": author,
            "isbn": isbn or None,
            "publisher": clean_value(result.get("publisher")) or None,
            "publication_year": result.get("publication_year") if result.get("publication_year") else None,
            "description": clean_value(result.get("description")) or f"Libro enriquecido automáticamente desde {result.get('source')}.",
            "cover_url": cover,
            "category_id": category_id,
            "price": None,
            "condition": clean_value(result.get("condition")) or None,
            "stock": result.get("stock") if result.get("stock") is not None else None,
            "published_flag": True,
        }
        resp = requests.post(
            f"{CATALOG_SERVICE_URL}/products/",
            json=payload,
            timeout=10,
        )
        if resp.status_code in [200, 201]:
            return {"status": "SYNCED", "catalog_book": resp.json()}
        return {
            "status": "FAILED",
            "catalog_status_code": resp.status_code,
            "catalog_response": resp.text,
        }
    except Exception as exc:
        return {"status": "ERROR", "message": str(exc)}


# ---------------------------------------------------------------------------
# Core enrichment logic (uses hexagonal DB models)
# ---------------------------------------------------------------------------

def enrich_book_logic(payload: dict, db: Session) -> dict:
    isbn = clean_isbn(payload.get("isbn") or "")
    title = clean_value(payload.get("title") or "")
    author = clean_value(payload.get("author") or "")
    cover_from_excel = clean_value(payload.get("cover") or "")
    condition = clean_value(payload.get("condition") or "")
    stock = clean_stock(payload.get("stock"))

    existing = catalog_book_exists(isbn, title)
    if existing:
        return {
            "enrichment_request_id": None,
            "source": "Existing Catalog",
            "title": existing.get("title"),
            "author": existing.get("author"),
            "publisher": existing.get("publisher"),
            "publication_year": existing.get("publication_year"),
            "description": existing.get("description"),
            "categories": [],
            "cover": existing.get("cover_url"),
            "condition": existing.get("condition"),
            "stock": existing.get("stock"),
            "confidence": "HIGH",
            "catalog_sync": {"status": "ALREADY_EXISTS", "catalog_book": existing},
        }

    book_id = isbn or normalize_text(title) or "unknown"
    req = EnrichmentRequestModel(
        book_id=book_id,
        isbn=isbn or None,
        title=title or None,
        author=author or None,
        status=EnrichmentStatusDB.processing,
    )
    db.add(req)
    try:
        db.commit()
        db.refresh(req)
    except Exception:
        db.rollback()
        raise

    google_result = None
    open_result = None

    if isbn or title:
        google_result = google_books_sync(isbn=isbn, title=title, author=author)
    if isbn:
        open_result = open_library_sync(isbn=isbn, title=title, author=author)

    fallback_result = {
        "source": "Fallback",
        "title": title or "Título no disponible",
        "author": author or "Autor no disponible",
        "publisher": None,
        "publication_year": None,
        "description": None,
        "cover": cover_from_excel,
        "categories": [],
        "confidence": "LOW",
    }

    # Merge sources — prefer Google Books, fill gaps from Open Library
    if google_result and open_result:
        result = google_result.copy()
        result["source"] = "Google Books + Open Library"
        for field in ["title", "author", "publisher", "publication_year", "description", "cover"]:
            if not clean_value(result.get(field)):
                result[field] = open_result.get(field)
        google_cats = google_result.get("categories") or []
        open_cats = open_result.get("categories") or []
        result["categories"] = list(dict.fromkeys(google_cats + open_cats))
        result["confidence"] = "HIGH"
    elif google_result:
        result = google_result
    elif open_result:
        result = open_result
    else:
        result = fallback_result

    if not clean_value(result.get("title")):
        result["title"] = title or "Título no disponible"
    if not clean_value(result.get("author")):
        result["author"] = author or "Autor no disponible"
    if not clean_value(result.get("cover")):
        result["cover"] = cover_from_excel or generate_placeholder_cover(result["title"])

    result["condition"] = condition
    result["stock"] = stock

    confidence_score = {"HIGH": 0.9, "MEDIUM": 0.6, "LOW": 0.3}.get(result.get("confidence", "LOW"), 0.3)

    save = EnrichmentResultModel(
        request_id=req.id,
        normalized_title=result["title"],
        normalized_author=result["author"],
        normalized_publisher=result.get("publisher"),
        normalized_description=result.get("description"),
        cover_url=result["cover"],
        confidence_score=confidence_score,
    )
    db.add(save)

    req.status = EnrichmentStatusDB.completed
    req.source_used = result["source"]
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    catalog_sync = sync_with_catalog(result, isbn)

    return {
        "enrichment_request_id": req.id,
        "source": result["source"],
        "title": result["title"],
        "author": result["author"],
        "publisher": result.get("publisher"),
        "publication_year": result.get("publication_year"),
        "description": result.get("description"),
        "categories": result.get("categories", []),
        "cover": result["cover"],
        "condition": result.get("condition"),
        "stock": result.get("stock"),
        "confidence": result.get("confidence"),
        "catalog_sync": catalog_sync,
    }


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/upload-excel")
def upload_excel(
    file: UploadFile = File(...),
    limit: int = 250,
    db: Session = Depends(get_db),
):
    file_bytes = file.file.read()
    inventory_sync = sync_excel_with_inventory(file_bytes, file.filename)

    import io
    df = pd.read_excel(io.BytesIO(file_bytes))
    if limit and limit > 0:
        df = df.head(limit)

    inserted = []
    duplicated = []
    errors = []
    processed_keys: set = set()

    for index, row in df.iterrows():
        try:
            isbn_13 = clean_isbn(row.get("ISBN 13") or "")
            isbn_10 = clean_isbn(row.get("ISBN 10") or "")
            issn = clean_isbn(row.get("ISSN") or "")

            title = clean_value(row.get("Título del libro") or "")
            cover = clean_value(row.get("URL PORTADA") or "")
            condition = clean_value(row.get("Estado del libro") or "")
            stock = clean_stock(row.get("unidades disponibles"))

            isbn = isbn_13 or isbn_10 or issn
            unique_key = isbn if isbn else normalize_text(title)

            if not unique_key:
                errors.append({"row": index + 1, "error": "Fila sin ISBN, ISSN ni título"})
                continue

            if unique_key in processed_keys:
                duplicated.append({
                    "row": index + 1,
                    "isbn": isbn,
                    "title": title,
                    "reason": "Duplicado dentro del Excel",
                })
                continue

            processed_keys.add(unique_key)

            payload = {
                "isbn": isbn,
                "title": title,
                "author": "",
                "cover": cover,
                "condition": condition,
                "stock": stock,
            }

            result = enrich_book_logic(payload, db)
            sync_status = result["catalog_sync"]["status"]

            if sync_status == "ALREADY_EXISTS":
                duplicated.append({
                    "row": index + 1,
                    "isbn": isbn,
                    "title": result["title"],
                    "reason": "Ya existe en catálogo",
                })
                continue

            if sync_status != "SYNCED":
                errors.append({
                    "row": index + 1,
                    "isbn": isbn,
                    "title": result["title"],
                    "error": result["catalog_sync"],
                })
                continue

            inserted.append({
                "row": index + 1,
                "isbn": isbn,
                "title": result["title"],
                "author": result["author"],
                "source": result["source"],
                "confidence": result["confidence"],
                "condition": result.get("condition"),
                "stock": result.get("stock"),
                "catalog_sync": sync_status,
            })

        except Exception as exc:
            errors.append({"row": index + 1, "error": str(exc)})

    return {
        "total_rows_processed": len(df),
        "inserted": len(inserted),
        "duplicated": len(duplicated),
        "errors": len(errors),
        "inventory_sync": inventory_sync,
        "inserted_preview": inserted[:20],
        "duplicated_preview": duplicated[:20],
        "error_preview": errors[:10],
    }
