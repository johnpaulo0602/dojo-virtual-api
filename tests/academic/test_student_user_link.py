import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.main import app
from src.core.database import get_db
from src.identity.models import User


@pytest.mark.asyncio
async def test_create_student_creates_user(get_db_session: AsyncSession, auth_token: str):
    """Creating a student should also create a User with role=aluno."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}
        res = await ac.post("/api/v1/students", json={
            "name": "Lucas Silva",
            "cpf": "12345678900",
            "birthDate": "2010-05-15",
            "gender": "masculino",
            "email": "lucas@teste.com",
            "beltName": "white_belt",
            "beltDegree": 0,
            "startDate": "2025-01-01",
        }, headers=headers)
        assert res.status_code == 201

        # Verify a User was created with the student's email
        stmt = select(User).where(User.email == "lucas@teste.com")
        result = await get_db_session.execute(stmt)
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.role == "aluno"
        assert user.name == "Lucas Silva"
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_student_duplicate_email_fails(get_db_session: AsyncSession, auth_token: str):
    """Creating two students with the same email should fail."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}
        res = await ac.post("/api/v1/students", json={
            "name": "Student One", "cpf": "11111111111",
            "birthDate": "2010-01-01", "gender": "masculino",
            "email": "same@teste.com", "beltName": "white_belt", "startDate": "2025-01-01",
        }, headers=headers)
        assert res.status_code == 201

        res = await ac.post("/api/v1/students", json={
            "name": "Student Two", "cpf": "22222222222",
            "birthDate": "2010-01-01", "gender": "feminino",
            "email": "same@teste.com", "beltName": "white_belt", "startDate": "2025-01-01",
        }, headers=headers)
        assert res.status_code == 400
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_student_requires_email(get_db_session: AsyncSession, auth_token: str):
    """Creating a student without email should return 422."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}
        res = await ac.post("/api/v1/students", json={
            "name": "No Email Student", "cpf": "33333333333",
            "birthDate": "2010-01-01", "gender": "masculino",
            "beltName": "white_belt", "startDate": "2025-01-01",
        }, headers=headers)
        assert res.status_code == 422
    app.dependency_overrides.clear()
