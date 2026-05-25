from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://bookflow:bookflow123@catalog-db:5432/catalog_db"

    class Config:
        env_file = ".env"


settings = Settings()
