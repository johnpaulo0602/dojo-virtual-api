"""Tests for role-based access control on financial, dashboard, and config endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.core.database import get_db
from src.identity.models import User
from src.core.security import get_password_hash, create_access_token


def _make_token(user: User) -> str:
    return create_access_token(data={"sub": str(user.id), "role": user.role})


async def _create_user(session: AsyncSession, role: str, email: str | None = None) -> tuple[User, str]:
    user = User(
        email=email or f"{role}@test.com",
        name=f"Test {role.title()}",
        hashed_password=get_password_hash("testpass"),
        role=role,
    )
    session.add(user)
    await session.flush()
    return user, _make_token(user)


# ---------------------------------------------------------------------------
# Financial: no auth -> 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_transactions_no_token_returns_401(get_db_session: AsyncSession):
    """Previously public endpoint must now require authentication."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/financial-transactions")
    app.dependency_overrides.clear()
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_list_donors_no_token_returns_401(get_db_session: AsyncSession):
    """Previously public endpoint must now require authentication."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/donors")
    app.dependency_overrides.clear()
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# Financial: instrutor -> 403
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_transactions_instrutor_returns_403(get_db_session: AsyncSession):
    """Financial endpoints are admin-only; instrutor must be denied."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "instrutor")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/financial-transactions", headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_list_donors_instrutor_returns_403(get_db_session: AsyncSession):
    """Financial endpoints are admin-only; instrutor must be denied."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "instrutor")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/donors", headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# Config: instrutor -> 403
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_config_categories_instrutor_returns_403(get_db_session: AsyncSession):
    """Config endpoints are admin-only; instrutor must be denied."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "instrutor")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/config/categories", headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# Dashboard: monitor -> 200
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_dashboard_summary_monitor_returns_200(get_db_session: AsyncSession):
    """Dashboard is accessible to admin, instrutor, and monitor."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "monitor")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/dashboard/summary", headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 200
