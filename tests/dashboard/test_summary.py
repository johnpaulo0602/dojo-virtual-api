import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app
from src.core.database import get_db
from src.academic.models import Student
from src.classes.models import ClassGroup, Lesson
from src.financial.models import FinancialTransaction, Donor
from datetime import date, time

@pytest.mark.asyncio
async def test_dashboard_summary(get_db_session: AsyncSession, auth_token: str):
    app.dependency_overrides[get_db] = lambda: get_db_session

    s1 = Student(name="A", cpf="111", matricula="M1", birth_date=date(2010, 1, 1), gender="M", belt_name="branca", status="ativo")
    s2 = Student(name="B", cpf="222", matricula="M2", birth_date=date(2011, 1, 1), gender="F", belt_name="branca", status="inativo")
    group = ClassGroup(name="T1", instructor_id="00000000-0000-0000-0000-000000000001", instructor_name="Prof", location="S1", capacity=20, status="ativa")
    get_db_session.add_all([s1, s2, group])
    await get_db_session.flush()

    lesson = Lesson(class_group_id=group.id, date=date.today(), start_time=time(9, 0), end_time=time(10, 0), location="S1", instructor_name="Prof")
    tx1 = FinancialTransaction(type="receita", category="mensalidade", description="M1", amount=100, date=date.today(), status="pago")
    tx2 = FinancialTransaction(type="despesa", category="material", description="M2", amount=50, date=date.today(), status="pago")
    donor = Donor(name="D1", email="d@t.com", phone="1", type="pessoa_fisica", document="1")
    get_db_session.add_all([lesson, tx1, tx2, donor])
    await get_db_session.flush()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {auth_token}"})
    app.dependency_overrides.clear()

    assert res.status_code == 200
    data = res.json()
    assert data["total_students"] == 2
    assert data["active_students"] == 1
    assert data["total_class_groups"] == 1
    assert data["active_class_groups"] == 1
    assert data["total_lessons_month"] == 1
    assert data["monthly_revenue"] == "100"
    assert data["monthly_expenses"] == "50"
    assert data["total_donors"] == 1
