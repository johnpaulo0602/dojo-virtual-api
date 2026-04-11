import pytest
from src.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_access_token

def test_password_hashing():
    pwd = "securepassword123"
    hashed = get_password_hash(pwd)
    assert pwd != hashed
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong", hashed) is False

def test_jwt_tokens():
    data = {"sub": "user-123", "role": "admin"}
    token = create_access_token(data)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "user-123"
    assert decoded["role"] == "admin"
    
    # refresh token is opaque string
    rt = create_refresh_token()
    assert isinstance(rt, str)
    assert len(rt) > 20