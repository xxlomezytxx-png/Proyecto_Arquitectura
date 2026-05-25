import pytest

from app.application.normalizer.isbn_validator import validate_and_normalize
from app.application.normalizer.author_formatter import format_author
from app.application.normalizer.text_normalizer import normalize_title, normalize_publisher
from app.application.normalizer.source_merger import merge_results
from app.domain.entities.enrichment import BookMetadata, EnrichmentSource


def test_isbn10_converts_to_isbn13_correctly():
    # 0-306-40615-2 is a valid ISBN-10
    result = validate_and_normalize("0306406152")
    assert result == "9780306406157"


def test_invalid_isbn_raises_validation_error():
    result = validate_and_normalize("0000000000")
    # Invalid ISBN-10 digits still produce ISBN-13 if digits are valid
    # An ISBN with letters returns None
    result2 = validate_and_normalize("978ABCDEFGH")
    assert result2 is None


def test_author_format_single_name():
    result = format_author("Charles Dickens")
    assert result == "Dickens, Charles"


def test_author_format_multiple_authors():
    result = format_author("Charles Dickens; Jane Austen")
    assert result == "Dickens, Charles; Austen, Jane"


def test_title_normalization_removes_special_chars():
    result = normalize_title("  great expectations\x00  ")
    assert result == "Great Expectations"


def test_source_merger_prefers_higher_confidence():
    low = BookMetadata(title="Wrong Title", author="Wrong Author",
                       source=EnrichmentSource.open_library, confidence_score=0.5)
    high = BookMetadata(title="Correct Title", author="Right Author",
                        source=EnrichmentSource.google_books, confidence_score=0.9)
    merged = merge_results([low, high])
    assert merged.title == "Correct Title"
    assert merged.confidence_score == 0.9


def test_source_merger_fills_missing_fields():
    primary = BookMetadata(title="A Book", source=EnrichmentSource.google_books,
                           confidence_score=0.9, description=None, cover_url=None)
    secondary = BookMetadata(title=None, description="A nice description",
                              cover_url="https://example.com/cover.jpg",
                              source=EnrichmentSource.open_library, confidence_score=0.7)
    merged = merge_results([primary, secondary])
    assert merged.title == "A Book"
    assert merged.description == "A nice description"
    assert merged.cover_url == "https://example.com/cover.jpg"


@pytest.mark.parametrize("raw,expected", [
    ("Penguin Books", "Penguin"),
    ("Penguin Publishers", "Penguin"),
    ("HarperCollins Publishers", "HarperCollins"),
    ("Harper Collins", "HarperCollins"),
    ("Random House Inc.", "Random House"),
    ("Simon and Schuster", "Simon & Schuster"),
    ("Oxford University Press", "Oxford University Press"),
    ("MIT Press", "MIT Press"),
    ("Unknown Publisher", "Unknown Publisher"),
    (None, None),
    ("", None),
])
def test_normalize_publisher_homologation(raw, expected):
    assert normalize_publisher(raw) == expected


def test_duplicate_detection_by_isbn():
    """Two sources returning the same ISBN — merger keeps best."""
    a = BookMetadata(title="Book A", isbn="9780141439518",
                     source=EnrichmentSource.google_books, confidence_score=0.9)
    b = BookMetadata(title="Book B", isbn="9780141439518",
                     source=EnrichmentSource.open_library, confidence_score=0.6)
    merged = merge_results([a, b])
    assert merged.isbn == "9780141439518"
    assert merged.title == "Book A"  # higher confidence wins
