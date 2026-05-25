from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class BookCondition(str, Enum):
    NUEVO = "NUEVO"
    BUENO = "BUENO"
    ACEPTABLE = "ACEPTABLE"
    DETERIORADO = "DETERIORADO"


@dataclass
class PricingReference:
    id: Optional[int]
    book_id: str
    source: str  # e.g., "eBay"
    price: float
    currency: str
    observed_at: datetime
    metadata: dict  # Additional info like item title, etc.


@dataclass
class PricingDecision:
    id: Optional[int]
    book_id: str
    condition: BookCondition
    base_price: float
    condition_factor: float
    suggested_price: float
    references_used: int
    source: str  # "external" or "fallback"
    explanation: str
    created_at: datetime
    book_title: Optional[str] = None
    references: List[PricingReference] = None