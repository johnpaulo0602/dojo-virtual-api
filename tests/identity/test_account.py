import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db

@pytest.mark.asyncio
async def test_update_profile(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.patch("/api/v1/auth/me", json={
            "name": "Novo Nome", "phone": "(11) 99999-1234",
        }, headers=headers)
        assert res.status_code == 200
        assert res.json()["name"] == "Novo Nome"
        assert res.json()["phone"] == "(11) 99999-1234"
        res = await ac.get("/api/v1/auth/me", headers=headers)
        assert res.json()["name"] == "Novo Nome"
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_change_password(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.put("/api/v1/auth/me/password", json={
            "current_password": "testpass", "new_password": "newpass123",
        }, headers=headers)
        assert res.status_code == 200
        res = await ac.put("/api/v1/auth/me/password", json={
            "current_password": "wrongpass", "new_password": "x",
        }, headers=headers)
        assert res.status_code == 400
    app.dependency_overrides.clear()
