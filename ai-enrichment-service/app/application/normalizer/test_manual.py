from app.domain.entities.enrichment import BookMetadata
from app.application.normalizer.source_merger import merge_results


def run_test():
    data = [
        BookMetadata(
            title="great expectations",
            author="Charles Dickens",
            publisher="Penguin",
            description="Libro clásico",
            cover_url=None,
            isbn="0141439513",  # ISBN-10
            publication_year=1861,
            source="google",
            confidence_score=0.9,
        ),
        BookMetadata(
            title="Great Expectations",
            author="Dickens, Charles",
            publisher=None,
            description=None,
            cover_url="http://image.com/book.jpg",
            isbn="9780141439518",  # ISBN-13 (mismo libro)
            publication_year=1861,
            source="openlibrary",
            confidence_score=0.8,
        ),
    ]

    result = merge_results(data)

    print("\nRESULTADO FINAL:\n")
    print(result)


if __name__ == "__main__":
    run_test()