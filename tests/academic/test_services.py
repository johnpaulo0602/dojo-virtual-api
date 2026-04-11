# api/tests/academic/test_services.py
import pytest
import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from src.academic.services import create_student_onboarding
from src.academic.schemas import StudentOnboarding, GuardianCreate, SchoolInfoCreate
from src.academic.models import School

@pytest.mark.asyncio
async def test_create_student_onboarding(get_db_session: AsyncSession):
    # Setup dummy school
    school = School(name="Test School", address="Test Addr")
    get_db_session.add(school)
    await get_db_session.flush()

    payload = StudentOnboarding(
        name="John Doe", cpf="123456", matricula="MAT1", birthDate=date(2010, 1, 1),
        gender="M", beltName="White", beltDegree=0,
        guardians=[GuardianCreate(name="Mom", cpf="654321", relationship="mae", phone="123")],
        schoolInfo=SchoolInfoCreate(schoolId=school.id)
    )

    student = await create_student_onboarding(get_db_session, payload)
    
    assert student.id is not None
    assert student.name == "John Doe"
    assert len(student.guardians) == 1
    assert student.school_info is not None
