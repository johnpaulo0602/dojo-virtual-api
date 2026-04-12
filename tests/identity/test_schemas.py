import uuid
import pytest
from pydantic import ValidationError
from src.identity.schemas import UserCreate, UserResponse, Token, RefreshTokenRequest

def test_user_create_valid():
    user = UserCreate(email="test@example.com", password="password123", role="user")
    assert user.email == "test@example.com"
    assert user.password == "password123"
    assert user.role == "user"

def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(email="invalid-email", password="password123", role="user")

def test_user_response_from_attributes():
    class MockUser:
        def __init__(self):
            self.id = uuid.uuid4()
            self.email = "test@example.com"
            self.name = "Test User"
            self.role = "user"
            self.phone = None
            self.belt_name = None
            self.belt_degree = None
            self.specialties = None
            self.status = "ativo"
            
    mock_user = MockUser()
    user_response = UserResponse.model_validate(mock_user)
    assert user_response.id == mock_user.id
    assert user_response.email == "test@example.com"
    assert user_response.role == "user"

def test_token_default_type():
    token = Token(access_token="access", refresh_token="refresh")
    assert token.token_type == "bearer"
    
def test_refresh_token_request():
    req = RefreshTokenRequest(refresh_token="refresh")
    assert req.refresh_token == "refresh"
