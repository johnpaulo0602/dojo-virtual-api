import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db

@pytest.mark.asyncio
async def test_categories_crud(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # GET returns default seed when no data exists
        res = await ac.get("/api/v1/config/categories", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "categories" in data
        assert len(data["categories"]) > 0

        # PUT replaces entire list
        new_cats = {
            "categories": [
                {"id": "c1", "name": "Doações", "type": "receita", "description": "Doações recebidas"},
                {"id": "c2", "name": "Material", "type": "despesa", "description": "Compra de material"},
            ]
        }
        res = await ac.put("/api/v1/config/categories", json=new_cats, headers=headers)
        assert res.status_code == 200
        assert len(res.json()["categories"]) == 2

        # GET returns what we just saved
        res = await ac.get("/api/v1/config/categories", headers=headers)
        cats = res.json()["categories"]
        assert len(cats) == 2
        assert cats[0]["name"] == "Doações"

        # PUT with empty list clears all
        res = await ac.put("/api/v1/config/categories", json={"categories": []}, headers=headers)
        assert res.status_code == 200
        assert len(res.json()["categories"]) == 0

    app.dependency_overrides.clear()
