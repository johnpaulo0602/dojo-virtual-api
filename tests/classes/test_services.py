# api/tests/classes/test_services.py
import pytest
import uuid
from datetime import time, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from src.classes.services import create_class_group, generate_lessons
from src.classes.schemas import ClassGroupCreate, ClassScheduleSchema, LessonGenerateRequest

@pytest.mark.asyncio
async def test_create_class_group(get_db_session: AsyncSession):
    payload = ClassGroupCreate(
        name="Kids", instructorId=uuid.uuid4(), instructorName="Sensei",
        location="Tatame 1", capacity=20,
        schedules=[ClassScheduleSchema(dayOfWeek=1, startTime=time(10, 0), endTime=time(11, 0))]
    )
    group = await create_class_group(get_db_session, payload)
    assert group.id is not None
    assert len(group.schedules) == 1

@pytest.mark.asyncio
async def test_generate_lessons(get_db_session: AsyncSession):
    payload = ClassGroupCreate(
        name="Kids", instructorId=uuid.uuid4(), instructorName="Sensei",
        location="Tatame 1", capacity=20,
        schedules=[ClassScheduleSchema(dayOfWeek=0, startTime=time(10, 0), endTime=time(11, 0))] # Monday
    )
    group = await create_class_group(get_db_session, payload)
    
    # Let's generate lessons for a week that starts on a Monday
    monday_date = date(2026, 4, 13)
    sunday_date = date(2026, 4, 19)
    req = LessonGenerateRequest(startDate=monday_date, endDate=sunday_date)
    
    lessons = await generate_lessons(get_db_session, group.id, req)
    assert len(lessons) == 1
    assert lessons[0].date == monday_date
