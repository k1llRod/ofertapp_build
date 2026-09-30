import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ofertapp Auth Service"
    PORT: int = int(os.getenv("PORT", "8001"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./auth.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ofertapp_super_secret_jwt_key_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

settings = Settings()
