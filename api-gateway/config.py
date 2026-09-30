import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ofertapp API Gateway"
    PORT: int = int(os.getenv("PORT", "8000"))
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    TRANSACTIONS_SERVICE_URL: str = os.getenv("TRANSACTIONS_SERVICE_URL", "http://localhost:8002")
    NOTIFICATIONS_SERVICE_URL: str = os.getenv("NOTIFICATIONS_SERVICE_URL", "http://localhost:8003")
    REPORTS_SERVICE_URL: str = os.getenv("REPORTS_SERVICE_URL", "http://localhost:8004")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ofertapp_super_secret_jwt_key_2026")
    ALGORITHM: str = "HS256"

settings = Settings()
