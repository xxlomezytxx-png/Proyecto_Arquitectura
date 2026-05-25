from abc import ABC, abstractmethod

from app.domain.entities.recommendation import RecommendedBook


class RecommendationStrategy(ABC):
    @abstractmethod
    async def recommend(
        self, book: dict, all_books: list[dict]
    ) -> list[RecommendedBook]: ...
