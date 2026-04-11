import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db
from src.classes.models import ClassGroup, ClassSchedule, Lesson
from datetime import date, time

@pytest.mark.asyncio
async def test_generate_lessons_endpoint(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    
    # Setup dummy group directly
    group = ClassGroup(
        name="Test API", instructor_id=uuid.uuid4(), instructor_name="Z",
        location="L", capacity=10
    )
    get_db_session.add(group)
    await get_db_session.flush()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(f"/api/v1/class-groups/{group.id}/lessons/generate", json={
            "startDate": "2026-04-01",
            "endDate": "2026-04-30"
        })
    
    app.dependency_overrides.clear()
    assert res.status_code == 201
    assert type(res.json()) is list

@pytest.mark.asyncio
async def test_get_classes_endpoints(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res_groups = await ac.get("/api/v1/class-groups")
        assert res_groups.status_code == 200
        assert type(res_groups.json()) is list

        res_lessons = await ac.get("/api/v1/class-groups/lessons")
        assert res_lessons.status_code == 200
        assert type(res_lessons.json()) is list

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_class_group_detail(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    group = ClassGroup(
        name="Turma Kids", instructor_id="00000000-0000-0000-0000-000000000001",
        instructor_name="Prof. Carlos", location="Sala 1", capacity=20,
    )
    get_db_session.add(group)
    await get_db_session.flush()
    schedule = ClassSchedule(class_group_id=group.id, day_of_week=1, start_time=time(9, 0), end_time=time(10, 0))
    get_db_session.add(schedule)
    await get_db_session.flush()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/class-groups/{group.id}", headers={"Authorization": f"Bearer {auth_token}"})
    app.dependency_overrides.clear()
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Turma Kids"
    assert len(data["schedules"]) == 1

@pytest.mark.asyncio
async def test_patch_class_group(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    group = ClassGroup(
        name="Turma Old", instructor_id="00000000-0000-0000-0000-000000000001",
        instructor_name="Prof. A", location="Sala 1", capacity=20,
    )
    get_db_session.add(group)
    await get_db_session.flush()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.patch(
            f"/api/v1/class-groups/{group.id}",
            json={"name": "Turma New", "capacity": 30},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
    app.dependency_overrides.clear()
    assert res.status_code == 200
    assert res.json()["name"] == "Turma New"
    assert res.json()["capacity"] == 30

@pytest.mark.asyncio
async def test_delete_class_group(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    group = ClassGroup(
        name="To Delete", instructor_id="00000000-0000-0000-0000-000000000001",
        instructor_name="Prof. A", location="Sala 1", capacity=20,
    )
    get_db_session.add(group)
    await get_db_session.flush()
    group_id = group.id
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.delete(f"/api/v1/class-groups/{group_id}", headers={"Authorization": f"Bearer {auth_token}"})
    app.dependency_overrides.clear()
    assert res.status_code == 204

@pytest.mark.asyncio
async def test_get_lesson_detail(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    group = ClassGroup(
        name="Turma A", instructor_id="00000000-0000-0000-0000-000000000001",
        instructor_name="Prof. A", location="Sala 1", capacity=20,
    )
    get_db_session.add(group)
    await get_db_session.flush()
    lesson = Lesson(
        class_group_id=group.id, date=date(2026, 4, 15),
        start_time=time(9, 0), end_time=time(10, 0),
        location="Sala 1", instructor_name="Prof. A", status="agendada",
    )
    get_db_session.add(lesson)
    await get_db_session.flush()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/class-groups/lessons/{lesson.id}", headers={"Authorization": f"Bearer {auth_token}"})
    app.dependency_overrides.clear()
    assert res.status_code == 200
    data = res.json()
    assert data["location"] == "Sala 1"
    assert data["class_group"]["name"] == "Turma A"
    assert data["attendance"] == []
