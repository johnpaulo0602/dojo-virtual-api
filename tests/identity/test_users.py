import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db
from src.identity.models import User
from src.core.security import get_password_hash

@pytest.mark.asyncio
async def test_list_users_by_role(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    instructor = User(email="inst@test.com", name="Instrutor A", hashed_password=get_password_hash("x"), role="instrutor")
    monitor = User(email="mon@test.com", name="Monitor B", hashed_password=get_password_hash("x"), role="monitor")
    get_db_session.add_all([instructor, monitor])
    await get_db_session.flush()

    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # All users
        res = await ac.get("/api/v1/users", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) == 3  # admin (from auth_token) + instructor + monitor

        # Filter by single role
        res = await ac.get("/api/v1/users?role=instrutor", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) == 1
        assert res.json()[0]["name"] == "Instrutor A"

        # Multiple roles
        res = await ac.get("/api/v1/users?role=instrutor,monitor", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) == 2
    app.dependency_overrides.clear()
