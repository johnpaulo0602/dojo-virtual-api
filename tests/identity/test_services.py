# api/tests/identity/test_services.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from src.identity.services import register_user, authenticate_user, create_user_session, refresh_user_session
from src.identity.schemas import UserCreate

@pytest.mark.asyncio
async def test_auth_flow(get_db_session: AsyncSession):
    # 1. Register User
    payload = UserCreate(email="test@example.com", password="password", role="admin")
    user = await register_user(get_db_session, payload)
    assert user.id is not None
    
    # 2. Authenticate
    auth_user = await authenticate_user(get_db_session, "test@example.com", "password")
    assert auth_user is not None
    assert auth_user.id == user.id
    
    # 3. Invalid Auth
    assert await authenticate_user(get_db_session, "test@example.com", "wrong") is None
    
    # 4. Create Session
    token_resp = await create_user_session(get_db_session, user)
    assert token_resp.access_token is not None
    assert token_resp.refresh_token is not None
    
    # 5. Refresh Session
    import asyncio
    await asyncio.sleep(1)
    new_token_resp = await refresh_user_session(get_db_session, token_resp.refresh_token)
    assert new_token_resp.access_token is not None
    assert new_token_resp.access_token != token_resp.access_token
    assert new_token_resp.refresh_token != token_resp.refresh_token
    
    # 6. Invalid Refresh
    with pytest.raises(HTTPException) as exc:
        await refresh_user_session(get_db_session, token_resp.refresh_token) # Old token is revoked/deleted
    assert exc.value.status_code == 401
