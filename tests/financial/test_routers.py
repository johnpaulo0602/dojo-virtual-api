import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db
from src.financial.models import Donor

@pytest.mark.asyncio
async def test_donation_endpoint(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session

    donor = Donor(name="Test", email="test@test.com", phone="123", type="pessoa_fisica", document="123")
    get_db_session.add(donor)
    await get_db_session.flush()

    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "amount": 250.00,
            "date": "2026-04-10",
            "method": "pix",
            "description": "Monthly contribution"
        }
        res = await ac.post(f"/api/v1/donors/{donor.id}/donations", json=payload, headers=headers)

    app.dependency_overrides.clear()
    assert res.status_code == 201
    data = res.json()
    assert "id" in data
    assert data["amount"] == "250.0"
    assert "transactionId" in data

@pytest.mark.asyncio
async def test_get_financial_endpoints(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res_transactions = await ac.get("/api/v1/financial-transactions", headers=headers)
        assert res_transactions.status_code == 200
        assert type(res_transactions.json()) is list

        res_donors = await ac.get("/api/v1/donors", headers=headers)
        assert res_donors.status_code == 200
        assert type(res_donors.json()) is list

    app.dependency_overrides.clear()
