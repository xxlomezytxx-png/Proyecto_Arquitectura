from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/enrichment/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_enrich_single():
    payload = {
        "book_reference": "REF-001",
        "title": "Cien Años de Soledad",
        "author": "Gabriel García Márquez",
        "isbn": "978-0-06-088328-7",
    }
    r = client.post("/enrichment/enrich", json=payload)
    assert r.status_code == 200

    data = r.json()

    assert data["book_reference"] == "REF-001"
    assert data["normalized_title"] == "Cien Años De Soledad"
    assert data["normalized_author"] == "Gabriel García Márquez"
    assert 0.65 <= data["confidence_score"] <= 1.0
    assert data["publication_year"] >= 1980
    assert data["source_used"] == "mock_google_books"
    assert data["metadata"]["isbn_verified"] is True

    assert "description" in data
    assert "category" in data
    assert "keywords" in data
    assert isinstance(data["keywords"], list)
    assert len(data["keywords"]) > 0


def test_enrich_single_deterministic():
    payload = {
        "book_reference": "REF-001",
        "title": "Cien Años de Soledad",
        "author": "Gabriel García Márquez",
    }
    r1 = client.post("/enrichment/enrich", json=payload)
    r2 = client.post("/enrichment/enrich", json=payload)

    assert r1.json()["confidence_score"] == r2.json()["confidence_score"]
    assert r1.json()["publication_year"] == r2.json()["publication_year"]
    assert r1.json()["category"] == r2.json()["category"]


def test_enrich_batch():
    payload = {
        "items": [
            {"book_reference": "REF-A", "title": "Don Quijote", "author": "Cervantes"},
            {"book_reference": "REF-B", "title": "La Odisea", "author": "Homero"},
        ]
    }
    r = client.post("/enrichment/enrich/batch", json=payload)
    assert r.status_code == 200

    data = r.json()
    assert len(data) == 2

    refs = {item["book_reference"] for item in data}
    assert refs == {"REF-A", "REF-B"}

    for item in data:
        assert "description" in item
        assert "category" in item
        assert "keywords" in item


def test_enrich_no_isbn():
    payload = {
        "book_reference": "REF-002",
        "title": "El Aleph",
        "author": "Jorge Luis Borges",
    }
    r = client.post("/enrichment/enrich", json=payload)
    assert r.status_code == 200
    assert r.json()["metadata"]["isbn_verified"] is False


def test_validation_error_when_title_is_empty():
    payload = {
        "book_reference": "REF-003",
        "title": "   ",
        "author": "Autor Demo"
    }
    r = client.post("/enrichment/enrich", json=payload)
    assert r.status_code == 422


def test_validation_error_when_author_is_empty():
    payload = {
        "book_reference": "REF-004",
        "title": "Libro Demo",
        "author": "   "
    }
    r = client.post("/enrichment/enrich", json=payload)
    assert r.status_code == 422


def test_validation_error_when_book_reference_is_empty():
    payload = {
        "book_reference": "   ",
        "title": "Libro Demo",
        "author": "Autor Demo"
    }
    r = client.post("/enrichment/enrich", json=payload)
    assert r.status_code == 422


def test_validation_error_when_isbn_is_invalid():
    payload = {
        "book_reference": "REF-005",
        "title": "Libro Demo",
        "author": "Autor Demo",
        "isbn": "ABC123"
    }
    r = client.post("/enrichment/enrich", json=payload)
    assert r.status_code == 422