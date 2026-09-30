import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ofertapp Reports Service"
    PORT: int = int(os.getenv("PORT", "8004"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./reports.db")
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    TRANSACTIONS_SERVICE_URL: str = os.getenv("TRANSACTIONS_SERVICE_URL", "http://localhost:8002")

settings = Settings()
