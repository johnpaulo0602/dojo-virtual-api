import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db
from src.core.security import get_password_hash, create_access_token
from src.identity.models import User


@pytest.mark.asyncio
async def test_register_requires_admin(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/auth/register", json={
            "email": "new@test.com", "password": "pass", "name": "New", "role": "monitor",
        })
        assert res.status_code == 401
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_forbidden_for_non_admin(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)

    monitor = User(
        email="monitor@test.com",
        name="Monitor",
        hashed_password=get_password_hash("testpass"),
        role="monitor",
    )
    get_db_session.add(monitor)
    await get_db_session.flush()
    token = create_access_token(data={"sub": str(monitor.id), "role": monitor.role})

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/auth/register", json={
            "email": "new@test.com", "password": "pass", "name": "New", "role": "monitor",
        }, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 403
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_allowed_for_admin(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/auth/register", json={
            "email": "new@test.com", "password": "pass", "name": "New", "role": "monitor",
        }, headers={"Authorization": f"Bearer {auth_token}"})
        assert res.status_code == 201
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_users_requires_admin(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/users")
        assert res.status_code == 401
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_users_forbidden_for_non_admin(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)

    instrutor = User(
        email="instrutor@test.com",
        name="Instrutor",
        hashed_password=get_password_hash("testpass"),
        role="instrutor",
    )
    get_db_session.add(instrutor)
    await get_db_session.flush()
    token = create_access_token(data={"sub": str(instrutor.id), "role": instrutor.role})

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 403
    app.dependency_overrides.clear()
