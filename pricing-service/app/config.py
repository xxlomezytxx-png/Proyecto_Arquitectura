from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://bookflow:bookflow123@pricing-db:5432/pricing_db"

    EBAY_API_URL: str = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    EBAY_APP_ID: str = ""

    CATALOG_SERVICE_URL: str = "http://catalog-service:8003"

    CACHE_TTL: int = 3600
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 60

    CURRENCY: str = "COP"
    USD_TO_COP: float = 4000
    MIN_PRICE_THRESHOLD: float = 10000

    CONDITION_FACTORS: dict = {
        "NUEVO": 1.0,
        "BUENO": 0.75,
        "ACEPTABLE": 0.50,
        "DETERIORADO": 0.25,
        "new": 1.0,
        "good": 0.75,
        "acceptable": 0.50,
        "poor": 0.25,
    }

    class Config:
        env_file = ".env"


settings = Settings()