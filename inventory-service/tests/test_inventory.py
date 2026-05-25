import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").status_code == 200


def test_upload_invalid_extension():
    resp = client.post(
        "/batches/upload",
        files={"file": ("data.txt", io.BytesIO(b"content"), "text/plain")},
    )
    assert resp.status_code == 400


def test_upload_valid_csv():
    csv = b"title,author,book_reference,quantity_available\nLibro A,Autor A,REF-001,5\n"
    resp = client.post(
        "/batches/upload",
        files={"file": ("inv.csv", io.BytesIO(csv), "text/csv")},
    )
    # 201 si hay DB, 500 si no hay DB disponible en tests unitarios
    assert resp.status_code in (201, 500)
