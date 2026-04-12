import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db
from src.academic.models import Student, Guardian, StudentSchoolInfo, StudentHealthProfile, School
from datetime import date


@pytest.mark.asyncio
async def test_get_student_detail(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session

    school = School(name="Escola Teste", address="Rua A, 123")
    get_db_session.add(school)
    await get_db_session.flush()

    student = Student(
        name="João Silva", cpf="12345678900", matricula="MAT001",
        birth_date=date(2010, 5, 15), gender="M", belt_name="branca", belt_degree=0,
    )
    get_db_session.add(student)
    await get_db_session.flush()

    guardian = Guardian(
        student_id=student.id, name="Maria Silva", cpf="98765432100",
        relationship_type="mae", phone="11999999999", is_primary=True,
    )
    school_info = StudentSchoolInfo(
        student_id=student.id, school_id=school.id,
        school_level="fundamental", school_year="5", school_shift="manha",
    )
    health = StudentHealthProfile(
        student_id=student.id, blood_type="O+",
    )
    get_db_session.add_all([guardian, school_info, health])
    await get_db_session.flush()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get(
            f"/api/v1/students/{student.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

    app.dependency_overrides.clear()
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "João Silva"
    assert len(data["guardians"]) == 1
    assert data["guardians"][0]["name"] == "Maria Silva"
    assert data["school_info"]["school_level"] == "fundamental"
    assert data["health_profile"]["blood_type"] == "O+"
    # New relation arrays should be present and empty
    assert data["emergency_contacts"] == []
    assert data["promotions"] == []
    assert data["contributions"] == []
    assert data["documents"] == []


@pytest.mark.asyncio
async def test_get_student_not_found(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get(
            "/api/v1/students/00000000-0000-0000-0000-000000000001",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
    app.dependency_overrides.clear()
    assert res.status_code == 404
