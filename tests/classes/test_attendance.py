import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db
from src.classes.models import ClassGroup, Lesson, AttendanceRecord
from src.academic.models import Student
from datetime import date, time

@pytest.mark.asyncio
async def test_batch_attendance(get_db_session: AsyncSession, auth_token: str):
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
        location="Sala 1", instructor_name="Prof. A",
    )
    get_db_session.add(lesson)
    await get_db_session.flush()
    s1 = Student(name="Aluno 1", cpf="11111111111", matricula="M001", birth_date=date(2010, 1, 1), gender="M", belt_name="branca")
    s2 = Student(name="Aluno 2", cpf="22222222222", matricula="M002", birth_date=date(2011, 2, 2), gender="F", belt_name="branca")
    get_db_session.add_all([s1, s2])
    await get_db_session.flush()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}
        # POST batch
        res = await ac.post(
            f"/api/v1/class-groups/lessons/{lesson.id}/attendance",
            json={"records": [
                {"student_id": str(s1.id), "present": True},
                {"student_id": str(s2.id), "present": False},
            ]},
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 2
        # GET attendance
        res = await ac.get(f"/api/v1/class-groups/lessons/{lesson.id}/attendance", headers=headers)
        assert res.status_code == 200
        records = res.json()
        assert len(records) == 2
        present_record = next(r for r in records if r["student_name"] == "Aluno 1")
        assert present_record["present"] is True
        # PATCH toggle
        record_id = records[0]["id"]
        res = await ac.patch(
            f"/api/v1/class-groups/attendance/{record_id}",
            json={"present": not records[0]["present"]},
            headers=headers,
        )
        assert res.status_code == 200
        assert res.json()["present"] != records[0]["present"]
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_batch_attendance_upsert(get_db_session: AsyncSession, auth_token: str):
    """Sending batch a second time should update, not duplicate."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    group = ClassGroup(
        name="Turma B", instructor_id="00000000-0000-0000-0000-000000000001",
        instructor_name="Prof. B", location="Sala 2", capacity=20,
    )
    get_db_session.add(group)
    await get_db_session.flush()
    lesson = Lesson(
        class_group_id=group.id, date=date(2026, 4, 16),
        start_time=time(10, 0), end_time=time(11, 0),
        location="Sala 2", instructor_name="Prof. B",
    )
    s1 = Student(name="Aluno X", cpf="33333333333", matricula="M003", birth_date=date(2010, 1, 1), gender="M", belt_name="branca")
    get_db_session.add_all([lesson, s1])
    await get_db_session.flush()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}
        # First save: present=False
        await ac.post(
            f"/api/v1/class-groups/lessons/{lesson.id}/attendance",
            json={"records": [{"student_id": str(s1.id), "present": False}]},
            headers=headers,
        )
        # Second save: present=True (upsert)
        res = await ac.post(
            f"/api/v1/class-groups/lessons/{lesson.id}/attendance",
            json={"records": [{"student_id": str(s1.id), "present": True}]},
            headers=headers,
        )
        assert res.status_code == 200
        # Verify only one record, and it's present=True
        res = await ac.get(f"/api/v1/class-groups/lessons/{lesson.id}/attendance", headers=headers)
        records = res.json()
        assert len(records) == 1
        assert records[0]["present"] is True
    app.dependency_overrides.clear()
