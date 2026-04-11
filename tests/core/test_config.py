# api/tests/core/test_config.py
from src.core.config import settings

def test_settings_load_database_url():
    # pydantic-settings loads from env automatically, but we can verify the default
    # or that it parses correctly. For now, verify the default connection string
    # structure matches what we expect from the docker-compose.
    assert "postgresql+asyncpg://" in settings.DATABASE_URL
    assert "postgres:92d5610b7538427a7268173f@localhost:5432/postgres" in settings.DATABASE_URL
