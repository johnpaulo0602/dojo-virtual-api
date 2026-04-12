import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db
from src.academic.models import Student
from datetime import date


async def _create_student(session, name="Test Student", cpf="12345678901"):
    student = Student(
        name=name, cpf=cpf, matricula=f"MAT{cpf[:5]}",
        birth_date=date(2010, 1, 1), gender="M",
        belt_name="branca", belt_degree=0,
    )
    session.add(student)
    await session.flush()
    return student


@pytest.mark.asyncio
async def test_emergency_contacts_crud(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    student = await _create_student(get_db_session)
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create
        res = await ac.post(f"/api/v1/students/{student.id}/emergency-contacts", json={
            "name": "Maria", "phone": "11999999999", "relationship_type": "mae",
        }, headers=headers)
        assert res.status_code == 201
        contact_id = res.json()["id"]

        # List
        res = await ac.get(f"/api/v1/students/{student.id}/emergency-contacts", headers=headers)
        assert len(res.json()) == 1

        # Delete
        res = await ac.delete(f"/api/v1/students/{student.id}/emergency-contacts/{contact_id}", headers=headers)
        assert res.status_code == 204

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_promotions(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    student = await _create_student(get_db_session, cpf="99999999999")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(f"/api/v1/students/{student.id}/promotions", json={
            "previous_belt": "branca", "previous_degree": 0,
            "new_belt": "branca", "new_degree": 1,
            "promoted_by": "Prof. Silva", "date": "2026-04-01",
        }, headers=headers)
        assert res.status_code == 201

        res = await ac.get(f"/api/v1/students/{student.id}/promotions", headers=headers)
        assert len(res.json()) == 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_contributions(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    student = await _create_student(get_db_session, cpf="88888888888")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(f"/api/v1/students/{student.id}/contributions", json={
            "reference": "Mar/2026", "amount": "50.00",
            "date": "2026-03-15", "method": "pix",
        }, headers=headers)
        assert res.status_code == 201

        res = await ac.get(f"/api/v1/students/{student.id}/contributions", headers=headers)
        assert len(res.json()) == 1
        assert res.json()[0]["reference"] == "Mar/2026"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_student_update(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session
    student = await _create_student(get_db_session, cpf="77777777777")
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {auth_token}"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.patch(f"/api/v1/students/{student.id}", json={
            "profession": "Engenheiro",
            "contributes": True,
            "contribution_amount": "100.00",
        }, headers=headers)
        assert res.status_code == 200
        assert res.json()["profession"] == "Engenheiro"
        assert res.json()["contributes"] is True

    app.dependency_overrides.clear()
