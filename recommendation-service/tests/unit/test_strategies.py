import asyncio

import pytest

from app.domain.strategies.author_similarity import AuthorSimilarityStrategy
from app.domain.strategies.category_similarity import CategorySimilarityStrategy


BOOK_A = {"id": "a", "title": "Book A", "author": "Martin Fowler", "category_id": "tech"}
BOOK_B = {"id": "b", "title": "Book B", "author": "Martin Fowler", "category_id": "tech"}
BOOK_C = {"id": "c", "title": "Book C", "author": "Kent Beck", "category_id": "tech"}
BOOK_D = {"id": "d", "title": "Book D", "author": "Kent Beck", "category_id": "fiction"}

ALL_BOOKS = [BOOK_A, BOOK_B, BOOK_C, BOOK_D]


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_author_similarity_finds_same_author():
    strategy = AuthorSimilarityStrategy()
    results = run(strategy.recommend(BOOK_A, ALL_BOOKS))
    ids = [r.book_id for r in results]
    assert "b" in ids
    assert "a" not in ids


def test_author_similarity_excludes_different_author():
    strategy = AuthorSimilarityStrategy()
    results = run(strategy.recommend(BOOK_A, ALL_BOOKS))
    ids = [r.book_id for r in results]
    assert "c" not in ids
    assert "d" not in ids


def test_author_similarity_empty_author():
    strategy = AuthorSimilarityStrategy()
    book_no_author = {"id": "x", "title": "No Author", "author": "", "category_id": "tech"}
    results = run(strategy.recommend(book_no_author, ALL_BOOKS))
    assert results == []


def test_category_similarity_finds_same_category():
    strategy = CategorySimilarityStrategy()
    results = run(strategy.recommend(BOOK_A, ALL_BOOKS))
    ids = [r.book_id for r in results]
    assert "b" in ids
    assert "c" in ids


def test_category_similarity_excludes_different_category():
    strategy = CategorySimilarityStrategy()
    results = run(strategy.recommend(BOOK_A, ALL_BOOKS))
    ids = [r.book_id for r in results]
    assert "d" not in ids


def test_category_similarity_excludes_source_book():
    strategy = CategorySimilarityStrategy()
    results = run(strategy.recommend(BOOK_A, ALL_BOOKS))
    ids = [r.book_id for r in results]
    assert "a" not in ids


def test_category_similarity_score_is_08():
    strategy = CategorySimilarityStrategy()
    results = run(strategy.recommend(BOOK_A, ALL_BOOKS))
    for r in results:
        assert r.score == 0.8


def test_author_similarity_score_is_10():
    strategy = AuthorSimilarityStrategy()
    results = run(strategy.recommend(BOOK_A, ALL_BOOKS))
    for r in results:
        assert r.score == 1.0