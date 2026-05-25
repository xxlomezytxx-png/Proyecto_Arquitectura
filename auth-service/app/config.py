import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://bookflow:bookflow123@auth-db:5432/auth_db"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    BFF_ORIGIN: str = "http://localhost:8000"
    APP_VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY env var is required and must not be empty")


settings = Settings()
