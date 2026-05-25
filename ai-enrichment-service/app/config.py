import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://bookflow:bookflow123@enrichment-db:5432/enrichment_db"
    )
    CATALOG_SERVICE_URL: str = os.getenv(
        "CATALOG_SERVICE_URL",
        "http://catalog-service:8003"
    )
    GOOGLE_BOOKS_API_KEY: str = os.getenv("GOOGLE_BOOKS_API_KEY", "")
    OPEN_LIBRARY_BASE_URL: str = os.getenv(
        "OPEN_LIBRARY_BASE_URL", "https://openlibrary.org"
    )
    CROSSREF_BASE_URL: str = os.getenv(
        "CROSSREF_BASE_URL", "https://api.crossref.org"
    )
    PORT: int = int(os.getenv("PORT", "8004"))


settings = Settings()

# Legacy aliases kept for backward compatibility
DATABASE_URL = settings.DATABASE_URL
CATALOG_SERVICE_URL = settings.CATALOG_SERVICE_URL
PORT = settings.PORT
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://inventory-service:8002")