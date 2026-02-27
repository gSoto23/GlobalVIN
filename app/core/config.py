from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "GlobalVIN API"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./globalvin.db"
    
    # Authentication JWT
    SECRET_KEY: str = "super_secret_key_for_development_only_12345"
    ALGORITHM: str = "HS256"
    
    # External APIs
    VINAUDIT_API_KEY: str = ""
    CARAPIS_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
