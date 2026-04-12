import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db

@pytest.mark.asyncio
async def test_school_crud(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # CREATE
        res = await ac.post("/api/v1/students/schools", json={
            "name": "Escola Nova", "address": "Rua A, 123",
        }, headers=headers)
        assert res.status_code == 201
        school_id = res.json()["id"]
        assert res.json()["name"] == "Escola Nova"

        # Verify it appears in list
        res = await ac.get("/api/v1/students/schools", headers=headers)
        assert len(res.json()) == 1

        # PATCH
        res = await ac.patch(f"/api/v1/students/schools/{school_id}", json={
            "name": "Escola Atualizada",
        }, headers=headers)
        assert res.status_code == 200
        assert res.json()["name"] == "Escola Atualizada"
        assert res.json()["address"] == "Rua A, 123"

        # DELETE
        res = await ac.delete(f"/api/v1/students/schools/{school_id}", headers=headers)
        assert res.status_code == 204

        # Verify deleted
        res = await ac.get("/api/v1/students/schools", headers=headers)
        assert len(res.json()) == 0

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_school_not_found(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.patch(
            "/api/v1/students/schools/00000000-0000-0000-0000-000000000001",
            json={"name": "X"}, headers=headers,
        )
        assert res.status_code == 404

        res = await ac.delete(
            "/api/v1/students/schools/00000000-0000-0000-0000-000000000001",
            headers=headers,
        )
        assert res.status_code == 404

    app.dependency_overrides.clear()
