"""Tests for role-based access control on academic endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from src.main import app
from src.core.database import get_db
from src.identity.models import User
from src.core.security import get_password_hash, create_access_token
from src.academic.models import Student


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


async def _create_student(session: AsyncSession) -> Student:
    student = Student(
        name="Test Student", cpf="12345678901", matricula="MAT12345",
        birth_date=date(2010, 1, 1), gender="M",
        belt_name="branca", belt_degree=0,
    )
    session.add(student)
    await session.flush()
    return student


# ---------------------------------------------------------------------------
# 1) Public access (no token) returns 401
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_students_no_token_returns_401(get_db_session: AsyncSession):
    """Previously public endpoint must now require authentication."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/students")
    app.dependency_overrides.clear()
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_onboard_student_no_token_returns_401(get_db_session: AsyncSession):
    """Previously public endpoint must now require authentication."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/students", json={
            "name": "X", "cpf": "000", "birthDate": "2010-01-01",
            "gender": "M", "beltName": "branca", "beltDegree": 0, "startDate": "2026-01-01",
        })
    app.dependency_overrides.clear()
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_list_schools_no_token_returns_401(get_db_session: AsyncSession):
    """Previously public endpoint must now require authentication."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/students/schools")
    app.dependency_overrides.clear()
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# 2) Monitor can read students but cannot create students
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_monitor_can_list_students(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "monitor")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/students", headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_monitor_cannot_create_student(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "monitor")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/students", json={
            "name": "X", "cpf": "000", "birthDate": "2010-01-01",
            "gender": "M", "beltName": "branca", "beltDegree": 0, "startDate": "2026-01-01",
        }, headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# 3) Instrutor can create students
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_instrutor_can_create_student(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "instrutor")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/students", json={
            "name": "New Student", "cpf": "99988877766",
            "birthDate": "2012-06-15", "gender": "F",
            "beltName": "branca", "beltDegree": 0, "startDate": "2026-03-01",
        }, headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 201
    assert res.json()["name"] == "New Student"


# ---------------------------------------------------------------------------
# 4) Contributions are admin-only
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_instrutor_cannot_access_contributions(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "instrutor")
    student = await _create_student(get_db_session)
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/students/{student.id}/contributions", headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_access_contributions(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "admin")
    student = await _create_student(get_db_session)
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/students/{student.id}/contributions", headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 200


# ---------------------------------------------------------------------------
# 5) Schools write is admin-only
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_instrutor_cannot_create_school(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "instrutor")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/students/schools", json={
            "name": "Escola Teste", "address": "Rua X",
        }, headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_create_school(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "admin")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/students/schools", json={
            "name": "Escola Teste", "address": "Rua X",
        }, headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 201


# ---------------------------------------------------------------------------
# 6) Monitor can read promotions/feedbacks but cannot write
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_monitor_can_read_promotions(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "monitor")
    student = await _create_student(get_db_session)
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/students/{student.id}/promotions", headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_monitor_cannot_create_promotion(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "monitor")
    student = await _create_student(get_db_session)
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(f"/api/v1/students/{student.id}/promotions", json={
            "previous_belt": "branca", "previous_degree": 0,
            "new_belt": "branca", "new_degree": 1,
            "promoted_by": "Prof. Silva", "date": "2026-04-01",
        }, headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# 7) Monitor cannot access schools (read requires admin/instrutor)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_monitor_cannot_list_schools(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "monitor")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/students/schools", headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# 8) Instrutor can read schools
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_instrutor_can_list_schools(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "instrutor")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/students/schools", headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 200
