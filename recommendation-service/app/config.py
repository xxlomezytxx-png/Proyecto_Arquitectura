import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CATALOG_SERVICE_URL: str = os.getenv(
        "CATALOG_SERVICE_URL", "http://catalog-service:8003"
    )
    INVENTORY_SERVICE_URL: str = os.getenv(
        "INVENTORY_SERVICE_URL", "http://inventory-service:8001"
    )
    HTTP_TIMEOUT: float = float(os.getenv("HTTP_TIMEOUT", "5.0"))
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8012"))
    MAX_RECOMMENDATIONS: int = int(os.getenv("MAX_RECOMMENDATIONS", "10"))

    class Config:
        env_file = ".env"

settings = Settings()