from app.domain.entities.recommendation import RecommendedBook
from app.domain.strategies.base import RecommendationStrategy


class CategorySimilarityStrategy(RecommendationStrategy):
    async def recommend(
        self, book: dict, all_books: list[dict]
    ) -> list[RecommendedBook]:
        source_category = book.get("category_id")
        if source_category is None:
            return []

        results: list[RecommendedBook] = []
        for candidate in all_books:
            if candidate.get("id") == book.get("id"):
                continue
            if candidate.get("category_id") == source_category:
                category_label = str(source_category)
                results.append(
                    RecommendedBook(
                        book_id=str(candidate["id"]),
                        title=candidate.get("title", ""),
                        author=candidate.get("author", ""),
                        category=category_label,
                        score=0.8,
                        reason=f"Same category: {category_label}",
                    )
                )
        return results
