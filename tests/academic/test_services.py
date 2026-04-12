# api/tests/academic/test_services.py
import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from src.academic.services import create_student_onboarding
from src.academic.schemas import StudentOnboarding


@pytest.mark.asyncio
async def test_create_student_onboarding(get_db_session: AsyncSession):
    payload = StudentOnboarding(
        name="John Doe",
        cpf="123456789",
        birthDate=date(2010, 1, 1),
        gender="M",
        beltName="branca",
        beltDegree=0,
        startDate=date(2026, 1, 1),
    )

    student = await create_student_onboarding(get_db_session, payload)

    assert student.id is not None
    assert student.name == "John Doe"
    assert student.belt_name == "branca"
    assert student.matricula is not None
    assert student.matricula.startswith("MAT")
