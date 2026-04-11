from datetime import datetime, timezone, timedelta
from src.identity.models import User, UserIdentity, RefreshToken

def test_user_model_instantiation():
    user = User(
        email="test@example.com",
        hashed_password="hashed_secret",
        role="admin"
    )
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_secret"
    assert user.role == "admin"

def test_user_identity_instantiation():
    identity = UserIdentity(
        provider="google",
        provider_id="12345"
    )
    assert identity.provider == "google"
    assert identity.provider_id == "12345"

def test_refresh_token_instantiation():
    expires = datetime.now(timezone.utc) + timedelta(days=7)
    token = RefreshToken(
        token="some_refresh_token",
        expires_at=expires
    )
    assert token.token == "some_refresh_token"
    assert token.expires_at == expires
