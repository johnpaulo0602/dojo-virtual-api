import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db
from src.core.security import get_password_hash
from src.identity.models import User


@pytest.mark.asyncio
async def test_auth_endpoints(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)

    admin = User(
        email="me@x.com",
        name="Admin",
        hashed_password=get_password_hash("123"),
        role="admin",
    )
    get_db_session.add(admin)
    await get_db_session.flush()

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Login
        res = await ac.post("/api/v1/auth/login", data={"username": "me@x.com", "password": "123"})
        assert res.status_code == 200
        tokens = res.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # 2. Get Me
        res = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
        assert res.status_code == 200
        assert res.json()["email"] == "me@x.com"

        # 3. Refresh
        res = await ac.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert res.status_code == 200
        new_refresh = res.json()["refresh_token"]

        # 4. Logout
        res = await ac.post("/api/v1/auth/logout", json={"refresh_token": new_refresh})
        assert res.status_code == 204

    app.dependency_overrides.clear()
