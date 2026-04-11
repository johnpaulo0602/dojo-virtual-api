from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Jiu-Jitsu Management API"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:92d5610b7538427a7268173f@localhost:5432/postgres"
    
    # JWT Config
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" # In prod, load from .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Initial Admin Setup
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()