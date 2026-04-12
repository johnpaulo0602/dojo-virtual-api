import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.main import app
from src.core.database import get_db
from src.identity.models import User


@pytest.mark.asyncio
async def test_first_access_success(get_db_session: AsyncSession, auth_token: str):
    """First access with valid email+CPF sets password and activates account."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}
        res = await ac.post("/api/v1/students", json={
            "name": "Aluno Teste", "cpf": "12345678900",
            "birthDate": "2010-01-01", "gender": "masculino",
            "email": "aluno@teste.com", "beltName": "white_belt",
            "startDate": "2025-01-01",
        }, headers=headers)
        assert res.status_code == 201

        res = await ac.post("/api/v1/auth/first-access", json={
            "email": "aluno@teste.com", "cpf": "12345678900",
            "new_password": "minhasenha123", "confirm_password": "minhasenha123",
        })
        assert res.status_code == 200

        res = await ac.post("/api/v1/auth/login", data={
            "username": "aluno@teste.com", "password": "minhasenha123",
        })
        assert res.status_code == 200
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_first_access_wrong_cpf(get_db_session: AsyncSession, auth_token: str):
    """First access with wrong CPF should return 400."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}
        await ac.post("/api/v1/students", json={
            "name": "Aluno CPF", "cpf": "11111111111",
            "birthDate": "2010-01-01", "gender": "masculino",
            "email": "alunocpf@teste.com", "beltName": "white_belt",
            "startDate": "2025-01-01",
        }, headers=headers)

        res = await ac.post("/api/v1/auth/first-access", json={
            "email": "alunocpf@teste.com", "cpf": "99999999999",
            "new_password": "senha123", "confirm_password": "senha123",
        })
        assert res.status_code == 400
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_first_access_already_activated(get_db_session: AsyncSession, auth_token: str):
    """First access on already-activated account should return 400."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}
        await ac.post("/api/v1/students", json={
            "name": "Aluno Ativado", "cpf": "22222222222",
            "birthDate": "2010-01-01", "gender": "masculino",
            "email": "ativado@teste.com", "beltName": "white_belt",
            "startDate": "2025-01-01",
        }, headers=headers)

        await ac.post("/api/v1/auth/first-access", json={
            "email": "ativado@teste.com", "cpf": "22222222222",
            "new_password": "senha123", "confirm_password": "senha123",
        })

        res = await ac.post("/api/v1/auth/first-access", json={
            "email": "ativado@teste.com", "cpf": "22222222222",
            "new_password": "outrasenha", "confirm_password": "outrasenha",
        })
        assert res.status_code == 400
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_first_access_password_mismatch(get_db_session: AsyncSession, auth_token: str):
    """First access with mismatched passwords should return 400."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {auth_token}"}
        await ac.post("/api/v1/students", json={
            "name": "Aluno Mismatch", "cpf": "33333333333",
            "birthDate": "2010-01-01", "gender": "masculino",
            "email": "mismatch@teste.com", "beltName": "white_belt",
            "startDate": "2025-01-01",
        }, headers=headers)

        res = await ac.post("/api/v1/auth/first-access", json={
            "email": "mismatch@teste.com", "cpf": "33333333333",
            "new_password": "senha123", "confirm_password": "senhadiferente",
        })
        assert res.status_code == 400
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_first_access_unknown_email(get_db_session: AsyncSession):
    """First access with nonexistent email should return 400."""
    app.dependency_overrides[get_db] = lambda: get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/auth/first-access", json={
            "email": "naoexiste@teste.com", "cpf": "00000000000",
            "new_password": "senha123", "confirm_password": "senha123",
        })
        assert res.status_code == 400
    app.dependency_overrides.clear()
