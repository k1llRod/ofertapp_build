import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ofertapp Notifications Service"
    PORT: int = int(os.getenv("PORT", "8003"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./notifications.db")
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

settings = Settings()
