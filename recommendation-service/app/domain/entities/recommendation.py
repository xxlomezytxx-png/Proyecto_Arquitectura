from dataclasses import dataclass


@dataclass(frozen=True)
class RecommendedBook:
    book_id: str
    title: str
    author: str
    category: str
    score: float
    reason: str
