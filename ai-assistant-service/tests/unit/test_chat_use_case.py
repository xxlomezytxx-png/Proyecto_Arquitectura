from unittest.mock import MagicMock

import pytest

from app.application.use_cases.chat_use_case import ChatUseCase, _detect_intent
from app.domain.entities.interaction import AssistantInteraction


def _make_use_case(
    repo=None, catalog=None, pricing=None, inventory=None
) -> ChatUseCase:
    repo = repo or MagicMock()
    catalog = catalog or MagicMock()
    pricing = pricing or MagicMock()
    inventory = inventory or MagicMock()
    return ChatUseCase(repo=repo, catalog=catalog, pricing=pricing, inventory=inventory)


def test_detect_intent_pricing():
    assert _detect_intent("¿Cuánto cuesta el libro?") == "pricing"


def test_detect_intent_inventory():
    assert _detect_intent("¿Hay disponibilidad?") == "inventory"


def test_detect_intent_catalog():
    assert _detect_intent("busca un libro de python") == "catalog"


def test_detect_intent_hardware_new_product_list():
    assert _detect_intent("Tienes nuevos monitores para streaming?") == "catalog_list"


def test_detect_intent_general():
    assert _detect_intent("hola") == "general"


def test_execute_saves_interaction():
    repo = MagicMock()
    saved = AssistantInteraction(
        id="abc",
        session_id="s1",
        user_question="hola",
        interpreted_intent="general",
        answer_text="Puedo ayudarte",
    )
    repo.save.return_value = saved

    uc = _make_use_case(repo=repo)
    result = uc.execute(session_id="s1", question="hola")

    assert repo.save.called
    assert result.session_id == "s1"
    assert result.interpreted_intent == "general"


def test_catalog_answer_no_books():
    catalog = MagicMock()
    catalog.search_books.return_value = []
    catalog.list_books.return_value = []
    uc = _make_use_case(catalog=catalog)
    answer = uc._answer_catalog("algo")
    assert "No encontré" in answer


def test_catalog_answer_with_books():
    catalog = MagicMock()
    catalog.search_books.return_value = [
        {"title": "Clean Code", "author": "Robert Martin"}
    ]
    uc = _make_use_case(catalog=catalog)
    answer = uc._answer_catalog("clean code")
    assert "Clean Code" in answer


def test_find_books_does_not_fallback_to_all_catalog_when_search_empty():
    catalog = MagicMock()
    catalog.search_books.return_value = []
    catalog.list_books.return_value = [{"title": "Clean Code"}]
    uc = _make_use_case(catalog=catalog)

    books = uc._find_books("nuevos monitores para streaming", limit=5)

    assert books == []


def test_pricing_answer_no_book():
    catalog = MagicMock()
    catalog.search_books.return_value = []
    uc = _make_use_case(catalog=catalog)
    answer = uc._answer_pricing("precio libro")
    assert "No encontré" in answer


def test_pricing_answer_with_price():
    catalog = MagicMock()
    catalog.search_books.return_value = [{"id": "b1", "title": "Clean Code"}]
    pricing = MagicMock()
    pricing.get_price.return_value = {"suggested_price": 12.5, "currency": "USD"}
    uc = _make_use_case(catalog=catalog, pricing=pricing)
    answer = uc._answer_pricing("precio clean code")
    assert "12.5" in answer


def test_inventory_answer_in_stock():
    inventory = MagicMock()
    inventory.list_items.return_value = [{"title": "Clean Code", "quantity_available": 5}]
    uc = _make_use_case(inventory=inventory)
    answer = uc._answer_inventory("disponible clean code")
    assert "disponible" in answer
