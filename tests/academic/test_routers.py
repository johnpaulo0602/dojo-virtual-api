import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db

@pytest.mark.asyncio
async def test_create_student_endpoint(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "name": "Test Student",
            "cpf": "12345678901",
            "birthDate": "2010-05-15",
            "gender": "M",
            "phone": "(11) 99999-0000",
            "beltName": "branca",
            "beltDegree": 0,
            "startDate": "2026-01-01",
        }
        response = await ac.post("/api/v1/students", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Student"
    assert data["belt_name"] == "branca"
    assert data["gender"] == "M"
    assert data["birth_date"] == "2010-05-15"
    assert data["status"] == "ativo"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_academic_endpoints(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res_students = await ac.get("/api/v1/students")
        assert res_students.status_code == 200
        assert type(res_students.json()) is list

        res_schools = await ac.get("/api/v1/students/schools")
        assert res_schools.status_code == 200
        assert type(res_schools.json()) is list

    app.dependency_overrides.clear()
