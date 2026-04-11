import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db

@pytest.mark.asyncio
async def test_donor_crud(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # CREATE
        res = await ac.post("/api/v1/donors", json={
            "name": "Carlos Souza", "email": "carlos@test.com",
            "phone": "11999999999", "type": "pessoa_fisica", "document": "12345678900",
        }, headers=headers)
        assert res.status_code == 201
        donor_id = res.json()["id"]

        # GET by ID (detail with donations)
        res = await ac.get(f"/api/v1/donors/{donor_id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["name"] == "Carlos Souza"
        assert data["donations"] == []
        assert data["total_donated"] == "0"

        # Create a donation for this donor
        res = await ac.post(f"/api/v1/donors/{donor_id}/donations", json={
            "amount": "500.00", "date": "2026-04-10", "method": "pix", "description": "Doação mensal",
        }, headers=headers)
        assert res.status_code == 201

        # GET detail again — should show donation
        res = await ac.get(f"/api/v1/donors/{donor_id}", headers=headers)
        data = res.json()
        assert len(data["donations"]) == 1
        assert data["total_donated"] == "500.0"

        # PATCH
        res = await ac.patch(f"/api/v1/donors/{donor_id}", json={
            "name": "Carlos Alberto Souza", "whatsapp": "11999999999",
        }, headers=headers)
        assert res.status_code == 200
        assert res.json()["name"] == "Carlos Alberto Souza"

        # DELETE
        res = await ac.delete(f"/api/v1/donors/{donor_id}", headers=headers)
        assert res.status_code == 204

    app.dependency_overrides.clear()
