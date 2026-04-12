"""Tests for role-based access control on classes endpoints."""
import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, time

from src.main import app
from src.core.database import get_db
from src.identity.models import User
from src.core.security import get_password_hash, create_access_token
from src.classes.models import ClassGroup, Lesson, AttendanceRecord
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


async def _create_group(session: AsyncSession) -> ClassGroup:
    group = ClassGroup(
        name="Turma RBAC", instructor_id=uuid.uuid4(),
        instructor_name="Prof. Test", location="Sala 1", capacity=20,
    )
    session.add(group)
    await session.flush()
    return group


async def _create_lesson(session: AsyncSession, group: ClassGroup) -> Lesson:
    lesson = Lesson(
        class_group_id=group.id, date=date(2026, 4, 15),
        start_time=time(9, 0), end_time=time(10, 0),
        location="Sala 1", instructor_name="Prof. Test", status="agendada",
    )
    session.add(lesson)
    await session.flush()
    return lesson


# ---------------------------------------------------------------------------
# 1) list_class_groups: no auth -> 401, monitor -> 200
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_class_groups_no_token_returns_401(get_db_session: AsyncSession):
    """Previously public endpoint must now require authentication."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/class-groups")
    app.dependency_overrides.clear()
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_list_class_groups_monitor_returns_200(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "monitor")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/class-groups", headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 200


# ---------------------------------------------------------------------------
# 2) create_group: monitor -> 403, instrutor -> 201
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_group_monitor_returns_403(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "monitor")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/class-groups", json={
            "name": "Turma X", "instructorId": str(uuid.uuid4()),
            "instructorName": "Prof. X", "location": "Sala 1", "capacity": 20,
        }, headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_create_group_instrutor_returns_201(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "instrutor")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/class-groups", json={
            "name": "Turma X", "instructorId": str(uuid.uuid4()),
            "instructorName": "Prof. X", "location": "Sala 1", "capacity": 20,
        }, headers=headers)
    app.dependency_overrides.clear()
    assert res.status_code == 201
    assert res.json()["name"] == "Turma X"


# ---------------------------------------------------------------------------
# 3) attendance: monitor -> allowed (not 403)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_attendance_monitor_allowed(get_db_session: AsyncSession):
    """Monitor should be able to save and read attendance."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "monitor")
    group = await _create_group(get_db_session)
    lesson = await _create_lesson(get_db_session, group)
    student = Student(
        name="Aluno RBAC", cpf="99988877766", matricula="MRBAC",
        birth_date=date(2010, 1, 1), gender="M", belt_name="branca",
    )
    get_db_session.add(student)
    await get_db_session.flush()

    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # POST batch attendance
        res = await ac.post(
            f"/api/v1/class-groups/lessons/{lesson.id}/attendance",
            json={"records": [{"student_id": str(student.id), "present": True}]},
            headers=headers,
        )
        assert res.status_code == 200

        # GET attendance
        res = await ac.get(
            f"/api/v1/class-groups/lessons/{lesson.id}/attendance",
            headers=headers,
        )
        assert res.status_code == 200

        # PATCH toggle attendance
        records = res.json()
        if records:
            res = await ac.patch(
                f"/api/v1/class-groups/attendance/{records[0]['id']}",
                json={"present": False},
                headers=headers,
            )
            assert res.status_code == 200

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 4) generate_lessons: monitor -> 403
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_generate_lessons_monitor_returns_403(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    _, token = await _create_user(get_db_session, "monitor")
    group = await _create_group(get_db_session)
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(
            f"/api/v1/class-groups/{group.id}/lessons/generate",
            json={"startDate": "2026-04-01", "endDate": "2026-04-30"},
            headers=headers,
        )
    app.dependency_overrides.clear()
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_generate_lessons_no_token_returns_401(get_db_session: AsyncSession):
    """Previously public endpoint must now require authentication."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    group = await _create_group(get_db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(
            f"/api/v1/class-groups/{group.id}/lessons/generate",
            json={"startDate": "2026-04-01", "endDate": "2026-04-30"},
        )
    app.dependency_overrides.clear()
    assert res.status_code == 401
