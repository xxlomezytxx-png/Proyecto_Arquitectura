"""Seed 20 enrichment requests (mix of statuses) with results for completed ones."""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.infrastructure.database.connection import SessionLocal, engine
from app.infrastructure.database.models import (Base, EnrichmentRequestModel,
                                                  EnrichmentResultModel,
                                                  EnrichmentStatusDB)

Base.metadata.create_all(bind=engine)

BOOKS = [
    {"book_id": "b001", "isbn": "9780061965487", "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "publisher": "Scribner"},
    {"book_id": "b002", "isbn": "9780140449136", "title": "Crime and Punishment", "author": "Fyodor Dostoevsky", "publisher": "Penguin Classics"},
    {"book_id": "b003", "isbn": "9780743273565", "title": "The Alchemist", "author": "Paulo Coelho", "publisher": "HarperOne"},
    {"book_id": "b004", "isbn": "9780062315007", "title": "To Kill a Mockingbird", "author": "Harper Lee", "publisher": "Harper Perennial"},
    {"book_id": "b005", "isbn": "9780316769174", "title": "The Catcher in the Rye", "author": "J.D. Salinger", "publisher": "Little, Brown"},
    {"book_id": "b006", "isbn": "9780679720201", "title": "One Hundred Years of Solitude", "author": "Gabriel García Márquez", "publisher": "Harper Perennial"},
    {"book_id": "b007", "isbn": "9780743477109", "title": "Romeo and Juliet", "author": "William Shakespeare", "publisher": "Simon & Schuster"},
    {"book_id": "b008", "isbn": "9780374528379", "title": "Anna Karenina", "author": "Leo Tolstoy", "publisher": "Farrar, Straus and Giroux"},
    {"book_id": "b009", "isbn": "9780141187761", "title": "1984", "author": "George Orwell", "publisher": "Penguin Books"},
    {"book_id": "b010", "isbn": "9780547928227", "title": "The Hobbit", "author": "J.R.R. Tolkien", "publisher": "Houghton Mifflin Harcourt"},
    {"book_id": "b011", "isbn": "9780385490818", "title": "The Handmaid's Tale", "author": "Margaret Atwood", "publisher": "Anchor Books"},
    {"book_id": "b012", "isbn": "9780671870256", "title": "Brave New World", "author": "Aldous Huxley", "publisher": "Harper Perennial"},
    {"book_id": "b013", "isbn": "9780062409850", "title": "Don Quixote", "author": "Miguel de Cervantes", "publisher": "Ecco"},
    {"book_id": "b014", "isbn": "9780553213119", "title": "Moby-Dick", "author": "Herman Melville", "publisher": "Bantam Classics"},
    {"book_id": "b015", "isbn": "9780679720202", "title": "Lolita", "author": "Vladimir Nabokov", "publisher": "Vintage"},
    {"book_id": "b016", "isbn": "9780374523510", "title": "War and Peace", "author": "Leo Tolstoy", "publisher": "Farrar, Straus and Giroux"},
    {"book_id": "b017", "isbn": "9780765326355", "title": "The Name of the Wind", "author": "Patrick Rothfuss", "publisher": "DAW Books"},
    {"book_id": "b018", "isbn": "9780307474278", "title": "The Road", "author": "Cormac McCarthy", "publisher": "Vintage"},
    {"book_id": "b019", "isbn": "9781501156700", "title": "It", "author": "Stephen King", "publisher": "Scribner"},
    {"book_id": "b020", "isbn": "9780545010221", "title": "Harry Potter and the Deathly Hallows", "author": "J.K. Rowling", "publisher": "Scholastic"},
]

RESULTS = {
    "b001": {"title": "The Great Gatsby", "author": "Fitzgerald, F. Scott", "publisher": "Scribner", "description": "A story of wealth, love, and the American Dream in the Jazz Age.", "cover_url": "https://covers.openlibrary.org/b/isbn/9780061965487-L.jpg", "score": 0.95},
    "b002": {"title": "Crime and Punishment", "author": "Dostoevsky, Fyodor", "publisher": "Penguin Classics", "description": "A psychological novel about guilt and redemption in 19th century Russia.", "cover_url": "https://covers.openlibrary.org/b/isbn/9780140449136-L.jpg", "score": 0.93},
    "b003": {"title": "The Alchemist", "author": "Coelho, Paulo", "publisher": "HarperOne", "description": "A philosophical novel about following one's dreams and Personal Legend.", "cover_url": "https://covers.openlibrary.org/b/isbn/9780743273565-L.jpg", "score": 0.91},
    "b004": {"title": "To Kill a Mockingbird", "author": "Lee, Harper", "publisher": "Harper Perennial", "description": "A coming-of-age story confronting racial injustice in the American South.", "cover_url": "https://covers.openlibrary.org/b/isbn/9780062315007-L.jpg", "score": 0.97},
    "b005": {"title": "The Catcher in the Rye", "author": "Salinger, J.D.", "publisher": "Little, Brown", "description": "A teenager's disillusionment with the adult world in 1950s New York.", "cover_url": "https://covers.openlibrary.org/b/isbn/9780316769174-L.jpg", "score": 0.92},
    "b006": {"title": "One Hundred Years of Solitude", "author": "García Márquez, Gabriel", "publisher": "Harper Perennial", "description": "Magical realism epic following seven generations of the Buendía family.", "cover_url": "https://covers.openlibrary.org/b/isbn/9780679720201-L.jpg", "score": 0.96},
    "b007": {"title": "Romeo and Juliet", "author": "Shakespeare, William", "publisher": "Simon & Schuster", "description": "The timeless tragedy of star-crossed lovers in Renaissance Verona.", "cover_url": "https://covers.openlibrary.org/b/isbn/9780743477109-L.jpg", "score": 0.98},
    "b008": {"title": "Anna Karenina", "author": "Tolstoy, Leo", "publisher": "Farrar, Straus and Giroux", "description": "A tragic love story set against the backdrop of Russian high society.", "cover_url": "https://covers.openlibrary.org/b/isbn/9780374528379-L.jpg", "score": 0.94},
    "b009": {"title": "1984", "author": "Orwell, George", "publisher": "Penguin Books", "description": "A dystopian vision of totalitarian surveillance and thought control.", "cover_url": "https://covers.openlibrary.org/b/isbn/9780141187761-L.jpg", "score": 0.99},
    "b010": {"title": "The Hobbit", "author": "Tolkien, J.R.R.", "publisher": "Houghton Mifflin Harcourt", "description": "Bilbo Baggins' unexpected journey with dwarves to reclaim their mountain home.", "cover_url": "https://covers.openlibrary.org/b/isbn/9780547928227-L.jpg", "score": 0.97},
    "b011": {"title": "The Handmaid's Tale", "author": "Atwood, Margaret", "publisher": "Anchor Books", "description": "A dystopian tale of a woman in a theocratic totalitarian state.", "cover_url": "https://covers.openlibrary.org/b/isbn/9780385490818-L.jpg", "score": 0.95},
    "b012": {"title": "Brave New World", "author": "Huxley, Aldous", "publisher": "Harper Perennial", "description": "A dystopian novel depicting a future society engineered for happiness.", "cover_url": "https://covers.openlibrary.org/b/isbn/9780671870256-L.jpg", "score": 0.93},
}

STATUS_SEQUENCE = [
    EnrichmentStatusDB.completed,
    EnrichmentStatusDB.completed,
    EnrichmentStatusDB.completed,
    EnrichmentStatusDB.completed,
    EnrichmentStatusDB.completed,
    EnrichmentStatusDB.completed,
    EnrichmentStatusDB.completed,
    EnrichmentStatusDB.completed,
    EnrichmentStatusDB.completed,
    EnrichmentStatusDB.completed,
    EnrichmentStatusDB.completed,
    EnrichmentStatusDB.completed,
    EnrichmentStatusDB.pending,
    EnrichmentStatusDB.pending,
    EnrichmentStatusDB.pending,
    EnrichmentStatusDB.processing,
    EnrichmentStatusDB.processing,
    EnrichmentStatusDB.failed,
    EnrichmentStatusDB.failed,
    EnrichmentStatusDB.failed,
]

SOURCE_SEQUENCE = [
    "google_books", "google_books", "open_library", "google_books", "open_library",
    "google_books", "crossref", "open_library", "google_books", "google_books",
    "open_library", "google_books",
    None, None, None, None, None,
    None, None, None,
]

ERROR_MSGS = {
    17: "All external APIs timed out after 5 seconds",
    18: "Google Books returned 403 Forbidden; Open Library returned empty result; Crossref unreachable",
    19: "ISBN checksum invalid; title/author search returned no results",
}


def seed():
    db = SessionLocal()
    try:
        existing = db.query(EnrichmentRequestModel).count()
        if existing > 0:
            print(f"Seed already applied ({existing} records). Skipping.")
            return

        now = datetime.now(timezone.utc)
        request_ids = []

        for i, book in enumerate(BOOKS):
            status = STATUS_SEQUENCE[i]
            source = SOURCE_SEQUENCE[i]
            error = ERROR_MSGS.get(i)
            offset_hours = len(BOOKS) - i
            requested_at = now - timedelta(hours=offset_hours)

            req = EnrichmentRequestModel(
                book_id=book["book_id"],
                isbn=book["isbn"],
                title=book["title"],
                author=book["author"],
                publisher=book["publisher"],
                status=status,
                requested_at=requested_at,
                source_used=source,
                error_message=error,
            )
            db.add(req)
            db.flush()
            request_ids.append((req.id, book["book_id"], status, requested_at))

        db.commit()

        for req_id, book_id, status, requested_at in request_ids:
            if status != EnrichmentStatusDB.completed:
                continue
            result_data = RESULTS.get(book_id)
            if not result_data:
                continue
            result = EnrichmentResultModel(
                request_id=req_id,
                normalized_title=result_data["title"],
                normalized_author=result_data["author"],
                normalized_publisher=result_data["publisher"],
                normalized_description=result_data["description"],
                cover_url=result_data["cover_url"],
                confidence_score=result_data["score"],
                created_at=requested_at + timedelta(seconds=2),
            )
            db.add(result)

        db.commit()
        print(f"Seeded {len(BOOKS)} enrichment requests and {len(RESULTS)} results.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
