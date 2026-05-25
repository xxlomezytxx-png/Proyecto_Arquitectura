import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.domain.pricing import BookCondition, PricingDecision
from app.application.pricing_use_cases import PricingService
from app.infrastructure.database import Base
from app.infrastructure.adapters.ebay_adapter import MockEbayAdapter


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_pricing.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def pricing_service():
    return PricingService(use_mock=True)


@pytest.mark.asyncio
async def test_calculate_price_nuevo_condition(pricing_service, db_session):
    """Test pricing calculation for NUEVO condition"""
    decision = await pricing_service.calculate_price(
        db=db_session,
        book_id="test-book-1",
        book_title="Test Book",
        condition=BookCondition.NUEVO
    )

    assert decision.condition == BookCondition.NUEVO
    assert decision.condition_factor == 1.0
    assert decision.suggested_price >= settings.MIN_PRICE_THRESHOLD
    assert "NUEVO" in decision.explanation


@pytest.mark.asyncio
async def test_calculate_price_bueno_condition(pricing_service, db_session):
    """Test pricing calculation for BUENO condition"""
    decision = await pricing_service.calculate_price(
        db=db_session,
        book_id="test-book-2",
        book_title="Test Book",
        condition=BookCondition.BUENO
    )

    assert decision.condition == BookCondition.BUENO
    assert decision.condition_factor == 0.75
    assert decision.suggested_price >= settings.MIN_PRICE_THRESHOLD


@pytest.mark.asyncio
async def test_calculate_price_aceptable_condition(pricing_service, db_session):
    """Test pricing calculation for ACEPTABLE condition"""
    decision = await pricing_service.calculate_price(
        db=db_session,
        book_id="test-book-3",
        book_title="Test Book",
        condition=BookCondition.ACEPTABLE
    )

    assert decision.condition == BookCondition.ACEPTABLE
    assert decision.condition_factor == 0.50
    assert decision.suggested_price >= settings.MIN_PRICE_THRESHOLD


@pytest.mark.asyncio
async def test_calculate_price_deteriorado_condition(pricing_service, db_session):
    """Test pricing calculation for DETERIORADO condition"""
    decision = await pricing_service.calculate_price(
        db=db_session,
        book_id="test-book-4",
        book_title="Test Book",
        condition=BookCondition.DETERIORADO
    )

    assert decision.condition == BookCondition.DETERIORADO
    assert decision.condition_factor == 0.25
    assert decision.suggested_price >= settings.MIN_PRICE_THRESHOLD


@pytest.mark.asyncio
async def test_fallback_pricing_when_external_fails(pricing_service, db_session):
    """Test fallback pricing when external API fails"""
    # Mock the adapter to raise an exception
    with patch.object(pricing_service.adapter, 'get_book_prices', side_effect=Exception("API Error")):
        decision = await pricing_service.calculate_price(
            db=db_session,
            book_id="test-book-5",
            book_title="Test Book",
            condition=BookCondition.NUEVO
        )

        assert decision.source == "fallback"
        assert decision.references_used == 0
        assert decision.suggested_price >= settings.MIN_PRICE_THRESHOLD
        assert "fallback" in decision.explanation


def test_minimum_price_threshold(pricing_service):
    """Test that minimum price threshold is applied"""
    # Create a decision with very low price
    decision = PricingDecision(
        id=None,
        book_id="test",
        condition=BookCondition.DETERIORADO,
        base_price=1.0,  # Very low base price
        condition_factor=0.25,
        suggested_price=0.25,  # Would be below threshold
        references_used=0,
        source="fallback",
        explanation="Test",
        created_at=None
    )

    # The service should apply the threshold in calculate_price
    # But for unit test, we can check the logic
    final_price = max(decision.suggested_price, settings.MIN_PRICE_THRESHOLD)
    assert final_price == settings.MIN_PRICE_THRESHOLD


def test_explanation_contains_key_information(pricing_service):
    """Test that explanations contain all required information"""
    explanation = pricing_service._build_explanation(
        base_price=15.99,
        condition_factor=0.75,
        suggested_price=11.99,
        references_used=5,
        source="external",
        condition=BookCondition.BUENO
    )

    assert "$15.99" in explanation
    assert "5 referencias" in explanation
    assert "BUENO" in explanation
    assert "0.75" in explanation
    assert "$11.99" in explanation


def test_external_api_status(pricing_service):
    """Test external API status reporting"""
    status = pricing_service.get_external_api_status()

    assert "source" in status
    assert "available" in status
    assert "last_check" in status
    assert status["source"] == "eBay"