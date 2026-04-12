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
        assert user.password_set is False
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


@pytest.mark.asyncio
async def test_get_student_me(get_db_session: AsyncSession, auth_token: str):
    """GET /api/v1/students/me returns the student linked to the current aluno user."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        admin_headers = {"Authorization": f"Bearer {auth_token}"}
        res = await ac.post("/api/v1/students", json={
            "name": "Aluno Me", "cpf": "44444444444", "birthDate": "2008-03-10",
            "gender": "masculino", "email": "alunome@teste.com",
            "beltName": "white_belt", "startDate": "2025-01-01",
        }, headers=admin_headers)
        assert res.status_code == 201

        from src.core.security import create_access_token
        stmt = select(User).where(User.email == "alunome@teste.com")
        result = await get_db_session.execute(stmt)
        aluno_user = result.scalar_one()
        aluno_token = create_access_token(data={"sub": str(aluno_user.id), "role": "aluno"})

        res = await ac.get("/api/v1/students/me",
                           headers={"Authorization": f"Bearer {aluno_token}"})
        assert res.status_code == 200
        assert res.json()["name"] == "Aluno Me"
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_patch_student_me(get_db_session: AsyncSession, auth_token: str):
    """PATCH /api/v1/students/me allows aluno to update phone."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        admin_headers = {"Authorization": f"Bearer {auth_token}"}
        res = await ac.post("/api/v1/students", json={
            "name": "Aluno Patch", "cpf": "55555555555", "birthDate": "2008-03-10",
            "gender": "feminino", "email": "alunopatch@teste.com",
            "beltName": "white_belt", "startDate": "2025-01-01",
        }, headers=admin_headers)
        assert res.status_code == 201

        from src.core.security import create_access_token
        stmt = select(User).where(User.email == "alunopatch@teste.com")
        result = await get_db_session.execute(stmt)
        aluno_user = result.scalar_one()
        aluno_token = create_access_token(data={"sub": str(aluno_user.id), "role": "aluno"})

        res = await ac.patch("/api/v1/students/me", json={"phone": "(11) 99999-0000"},
                             headers={"Authorization": f"Bearer {aluno_token}"})
        assert res.status_code == 200
        assert res.json()["phone"] == "(11) 99999-0000"
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_student_me_non_aluno_rejected(get_db_session: AsyncSession, auth_token: str):
    """GET /api/v1/students/me with admin token should return 403."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/students/me",
                           headers={"Authorization": f"Bearer {auth_token}"})
        assert res.status_code == 403
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_student_detail_aluno_own_only(get_db_session: AsyncSession, auth_token: str):
    """Aluno can see own student but not others via GET /students/{id}."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        admin_headers = {"Authorization": f"Bearer {auth_token}"}

        res1 = await ac.post("/api/v1/students", json={
            "name": "Student A", "cpf": "66666666666", "birthDate": "2008-01-01",
            "gender": "masculino", "email": "studenta@teste.com",
            "beltName": "white_belt", "startDate": "2025-01-01",
        }, headers=admin_headers)
        student_a_id = res1.json()["id"]

        res2 = await ac.post("/api/v1/students", json={
            "name": "Student B", "cpf": "77777777777", "birthDate": "2008-01-01",
            "gender": "feminino", "email": "studentb@teste.com",
            "beltName": "white_belt", "startDate": "2025-01-01",
        }, headers=admin_headers)
        student_b_id = res2.json()["id"]

        from src.core.security import create_access_token
        stmt = select(User).where(User.email == "studenta@teste.com")
        result = await get_db_session.execute(stmt)
        aluno_a = result.scalar_one()
        aluno_a_token = create_access_token(data={"sub": str(aluno_a.id), "role": "aluno"})
        aluno_headers = {"Authorization": f"Bearer {aluno_a_token}"}

        res = await ac.get(f"/api/v1/students/{student_a_id}", headers=aluno_headers)
        assert res.status_code == 200

        res = await ac.get(f"/api/v1/students/{student_b_id}", headers=aluno_headers)
        assert res.status_code == 403
    app.dependency_overrides.clear()
