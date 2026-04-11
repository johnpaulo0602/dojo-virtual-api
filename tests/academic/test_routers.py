import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.academic.models import School
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db

@pytest.mark.asyncio
async def test_create_student_endpoint(get_db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: get_db_session
    # Setup dummy school
    school = School(name="Endpoint School", address="Endpoint Addr")
    get_db_session.add(school)
    await get_db_session.flush()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "name": "Jane Doe",
            "cpf": "111222333",
            "matricula": "MAT2",
            "birthDate": "2015-05-10",
            "gender": "F",
            "beltName": "Grey",
            "beltDegree": 1,
            "schoolInfo": {"schoolId": str(school.id)}
        }
        response = await ac.post("/api/v1/students", json=payload)
    
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["name"] == "Jane Doe"


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
