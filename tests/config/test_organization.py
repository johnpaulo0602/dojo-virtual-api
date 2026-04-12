import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db

@pytest.mark.asyncio
async def test_organization_settings(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/config/organization", headers=headers)
        assert res.status_code == 200
        assert res.json()["project_name"] == ""
        assert res.json()["socials"] == []
        settings = {
            "project_name": "Dojo Virtual", "email": "contato@dojo.org",
            "phone": "(11) 3000-0000", "address": "Rua do Esporte, 100",
            "description": "Sistema de gestão", "cnpj": "12.345.678/0001-90",
            "socials": [{"platform": "instagram", "url": "@dojovirtual"}],
            "managers": [{"name": "Carlos", "phone": "11999", "email": "c@d.org"}],
            "default_belt": "branca", "max_students_per_class": 30,
            "attendance_threshold": 80, "default_contribution": "100",
        }
        res = await ac.put("/api/v1/config/organization", json=settings, headers=headers)
        assert res.status_code == 200
        assert res.json()["project_name"] == "Dojo Virtual"
        res = await ac.get("/api/v1/config/organization", headers=headers)
        assert res.json()["cnpj"] == "12.345.678/0001-90"
        assert res.json()["max_students_per_class"] == 30
    app.dependency_overrides.clear()
