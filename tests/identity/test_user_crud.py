import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db

@pytest.mark.asyncio
async def test_create_user(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/users", json={
            "email": "inst@test.com", "name": "Instrutor Novo",
            "password": "senha123", "role": "instrutor",
            "belt_name": "preta", "belt_degree": 2,
            "specialties": "guarda,raspagem",
        }, headers=headers)
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "Instrutor Novo"
        assert data["role"] == "instrutor"
        assert data["belt_name"] == "preta"
        assert data["status"] == "ativo"
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_update_user(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/users", json={
            "email": "monitor@test.com", "name": "Monitor A",
            "password": "x", "role": "monitor",
        }, headers=headers)
        user_id = res.json()["id"]
        res = await ac.patch(f"/api/v1/users/{user_id}", json={
            "role": "instrutor", "status": "inativo", "belt_name": "marrom",
        }, headers=headers)
        assert res.status_code == 200
        assert res.json()["role"] == "instrutor"
        assert res.json()["status"] == "inativo"
        assert res.json()["belt_name"] == "marrom"
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_delete_user(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/users", json={
            "email": "todelete@test.com", "name": "Delete Me",
            "password": "x", "role": "monitor",
        }, headers=headers)
        user_id = res.json()["id"]
        res = await ac.delete(f"/api/v1/users/{user_id}", headers=headers)
        assert res.status_code == 204
        res = await ac.get("/api/v1/users?role=monitor", headers=headers)
        names = [u["name"] for u in res.json()]
        assert "Delete Me" not in names
    app.dependency_overrides.clear()
