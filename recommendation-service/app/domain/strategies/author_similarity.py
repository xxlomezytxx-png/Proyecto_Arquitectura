from app.domain.entities.recommendation import RecommendedBook
from app.domain.strategies.base import RecommendationStrategy


class AuthorSimilarityStrategy(RecommendationStrategy):
    async def recommend(
        self, book: dict, all_books: list[dict]
    ) -> list[RecommendedBook]:
        source_author = (book.get("author") or "").lower().strip()
        if not source_author:
            return []

        results: list[RecommendedBook] = []
        for candidate in all_books:
            if candidate.get("id") == book.get("id"):
                continue
            candidate_author = (candidate.get("author") or "").lower().strip()
            if not candidate_author:
                continue
            if source_author == candidate_author:
                results.append(
                    RecommendedBook(
                        book_id=str(candidate["id"]),
                        title=candidate.get("title", ""),
                        author=candidate.get("author", ""),
                        category=str(candidate.get("category_id", "")),
                        score=1.0,
                        reason=f"Same author: {candidate.get('author', '')}",
                    )
                )
        return results
