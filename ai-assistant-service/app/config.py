import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://bookflow:bookflow123@assistant-db:5432/assistant_db",
    )
    CATALOG_SERVICE_URL: str = os.getenv(
        "CATALOG_SERVICE_URL", "http://catalog-service:8003"
    )
    PRICING_SERVICE_URL: str = os.getenv(
        "PRICING_SERVICE_URL", "http://pricing-service:8005"
    )
    INVENTORY_SERVICE_URL: str = os.getenv(
        "INVENTORY_SERVICE_URL", "http://inventory-service:8002"
    )
    HTTP_TIMEOUT: float = float(os.getenv("HTTP_TIMEOUT", "5.0"))
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8011"))

    class Config:
        env_file = ".env"


settings = Settings()
