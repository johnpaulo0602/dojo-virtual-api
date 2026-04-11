import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db

@pytest.mark.asyncio
async def test_transaction_crud(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # CREATE
        res = await ac.post("/api/v1/financial-transactions", json={
            "type": "receita", "category": "mensalidade",
            "description": "Mensalidade Abril", "amount": "150.00",
            "date": "2026-04-10", "status": "pago",
        }, headers=headers)
        assert res.status_code == 201
        tx_id = res.json()["id"]

        # GET by ID
        res = await ac.get(f"/api/v1/financial-transactions/{tx_id}", headers=headers)
        assert res.status_code == 200
        assert res.json()["description"] == "Mensalidade Abril"

        # PATCH
        res = await ac.patch(f"/api/v1/financial-transactions/{tx_id}", json={
            "description": "Mensalidade Abril (atualizado)", "amount": "180.00",
        }, headers=headers)
        assert res.status_code == 200
        assert res.json()["description"] == "Mensalidade Abril (atualizado)"

        # DELETE
        res = await ac.delete(f"/api/v1/financial-transactions/{tx_id}", headers=headers)
        assert res.status_code == 204

        # Verify deleted
        res = await ac.get(f"/api/v1/financial-transactions/{tx_id}", headers=headers)
        assert res.status_code == 404

    app.dependency_overrides.clear()
