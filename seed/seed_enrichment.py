"""Seed enrichment requests and results into enrichment_db (matches the technology catalog items)."""
import datetime
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-enrichment-service"))

from app.infrastructure.database.connection import Base  # noqa: E402
from app.infrastructure.database.models import (  # noqa: E402
    EnrichmentRequestModel,
    EnrichmentResultModel,
    EnrichmentStatusDB,
)

DATABASE_URL = os.getenv(
    "ENRICHMENT_DATABASE_URL",
    "postgresql://bookflow:bookflow123@localhost:5432/enrichment_db",
)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

ENRICHMENTS = [
    {
        "book_id": "sku:rog-strix-pc-001",
        "isbn": "sku:rog-strix-pc-001",
        "title": "ASUS ROG Strix Gaming PC",
        "author": "ASUS",
        "publisher": "ROG Strix",
        "source_used": "internal_catalog",
        "normalized_title": "ASUS ROG Strix Gaming PC",
        "normalized_author": "ASUS",
        "normalized_publisher": "ROG Strix",
        "normalized_description": "PC gamer completo con GPU RTX 4080, CPU Intel Core i9, 32GB DDR5 y almacenamiento NVMe de 2TB.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
        "confidence_score": 0.95,
    },
    {
        "book_id": "sku:msi-aegis-ti5-002",
        "isbn": "sku:msi-aegis-ti5-002",
        "title": "MSI Aegis Ti5 Gaming PC",
        "author": "MSI",
        "publisher": "Aegis Ti5",
        "source_used": "internal_catalog",
        "normalized_title": "MSI Aegis Ti5 Gaming PC",
        "normalized_author": "MSI",
        "normalized_publisher": "Aegis Ti5",
        "normalized_description": "Estación de juego con procesador Intel Core i9, GPU NVIDIA y refrigeración líquida avanzada.",
        "cover_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1200&q=80",
        "confidence_score": 0.92,
    },
    {
        "book_id": "sku:flow-x16-003",
        "isbn": "sku:flow-x16-003",
        "title": "ASUS ROG Flow X16",
        "author": "ASUS",
        "publisher": "ROG",
        "source_used": "internal_catalog",
        "normalized_title": "ASUS ROG Flow X16",
        "normalized_author": "ASUS",
        "normalized_publisher": "ROG",
        "normalized_description": "Laptop convertible gamer con pantalla de 16 pulgadas, GPU RTX y procesador Intel de última generación.",
        "cover_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
        "confidence_score": 0.94,
    },
    {
        "book_id": "sku:alienware-x16-004",
        "isbn": "sku:alienware-x16-004",
        "title": "Dell Alienware x16",
        "author": "Dell",
        "publisher": "Alienware",
        "source_used": "internal_catalog",
        "normalized_title": "Dell Alienware x16",
        "normalized_author": "Dell",
        "normalized_publisher": "Alienware",
        "normalized_description": "Laptop premium para gaming con memoria DDR5, pantalla QHD y teclado retroiluminado.",
        "cover_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=1200&q=80",
        "confidence_score": 0.93,
    },
    {
        "book_id": "sku:rtx-4080-005",
        "isbn": "sku:rtx-4080-005",
        "title": "NVIDIA GeForce RTX 4080",
        "author": "NVIDIA",
        "publisher": "GeForce",
        "source_used": "internal_catalog",
        "normalized_title": "NVIDIA GeForce RTX 4080",
        "normalized_author": "NVIDIA",
        "normalized_publisher": "GeForce",
        "normalized_description": "Tarjeta gráfica de alto rendimiento para gaming 4K y creación de contenido intensiva.",
        "cover_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
        "confidence_score": 0.96,
    },
    {
        "book_id": "sku:rx-7900-006",
        "isbn": "sku:rx-7900-006",
        "title": "AMD Radeon RX 7900 XT",
        "author": "AMD",
        "publisher": "Radeon",
        "source_used": "internal_catalog",
        "normalized_title": "AMD Radeon RX 7900 XT",
        "normalized_author": "AMD",
        "normalized_publisher": "Radeon",
        "normalized_description": "GPU de alto rendimiento para gaming y renderizado en resoluciones altas.",
        "cover_url": "https://images.unsplash.com/photo-1591799265444-d66432b91588?auto=format&fit=crop&w=1200&q=80",
        "confidence_score": 0.95,
    },
]


def run() -> None:
    session = Session()
    try:
        seeded = 0
        for e in ENRICHMENTS:
            existing = session.query(EnrichmentRequestModel).filter_by(book_id=e["book_id"]).first()
            if existing:
                continue

            request = EnrichmentRequestModel(
                book_id=e["book_id"],
                isbn=e["isbn"],
                title=e["title"],
                author=e["author"],
                publisher=e["publisher"],
                source_used=e["source_used"],
                status=EnrichmentStatusDB.completed,
                requested_at=datetime.datetime.now(datetime.timezone.utc),
            )
            session.add(request)
            session.flush()

            result = EnrichmentResultModel(
                request_id=request.id,
                normalized_title=e["normalized_title"],
                normalized_author=e["normalized_author"],
                normalized_publisher=e["normalized_publisher"],
                normalized_description=e["normalized_description"],
                cover_url=e["cover_url"],
                confidence_score=e["confidence_score"],
                created_at=datetime.datetime.now(datetime.timezone.utc),
            )
            session.add(result)

            seeded += 1

        session.commit()
        print(f"Seeded {seeded} enrichment entries.")
    except Exception as exc:
        session.rollback()
        print(f"Seed failed: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run()
