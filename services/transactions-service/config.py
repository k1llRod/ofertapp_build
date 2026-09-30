import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ofertapp Transactions & Catalog Service"
    PORT: int = int(os.getenv("PORT", "8002"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./transactions.db")
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    NOTIFICATIONS_SERVICE_URL: str = os.getenv("NOTIFICATIONS_SERVICE_URL", "http://localhost:8003")

settings = Settings()
