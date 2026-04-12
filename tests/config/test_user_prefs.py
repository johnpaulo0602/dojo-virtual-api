import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db

@pytest.mark.asyncio
async def test_user_prefs(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/config/user_prefs", headers=headers)
        assert res.status_code == 200
        assert res.json()["notify_new_student"] is True
        res = await ac.put("/api/v1/config/user_prefs", json={
            "notify_new_student": False, "notify_attendance": True,
            "notify_financial": False, "notify_belt_promotion": True,
        }, headers=headers)
        assert res.status_code == 200
        assert res.json()["notify_new_student"] is False
        res = await ac.get("/api/v1/config/user_prefs", headers=headers)
        assert res.json()["notify_financial"] is False
    app.dependency_overrides.clear()
