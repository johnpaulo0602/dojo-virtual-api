import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db

@pytest.mark.asyncio
async def test_auth_endpoints(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Register
        res = await ac.post("/api/v1/auth/register", json={"email":"me@x.com", "password":"123", "role":"admin"})
        assert res.status_code == 201
        
        # 2. Login
        res = await ac.post("/api/v1/auth/login", data={"username":"me@x.com", "password":"123"})
        assert res.status_code == 200
        tokens = res.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # 3. Get Me
        res = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
        assert res.status_code == 200
        assert res.json()["email"] == "me@x.com"
        
        # 4. Refresh
        res = await ac.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert res.status_code == 200
        new_refresh = res.json()["refresh_token"]
        
        # 5. Logout
        res = await ac.post("/api/v1/auth/logout", json={"refresh_token": new_refresh})
        assert res.status_code == 204

    app.dependency_overrides.clear()