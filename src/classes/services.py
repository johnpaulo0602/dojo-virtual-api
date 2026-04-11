# api/src/classes/services.py
import uuid
from datetime import date, timedelta, datetime, timezone
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.classes.models import ClassGroup, ClassSchedule, Lesson, AttendanceRecord
from src.classes.schemas import ClassGroupCreate, LessonGenerateRequest
from src.academic.models import Student

async def create_class_group(db: AsyncSession, payload: ClassGroupCreate) -> ClassGroup:
    group_data = payload.model_dump(exclude={"schedules"})
    db_group = ClassGroup(**group_data)
    db.add(db_group)
    await db.flush()
    
    for sched_data in payload.schedules:
        db_sched = ClassSchedule(class_group_id=db_group.id, **sched_data.model_dump())
        db.add(db_sched)
        
    await db.flush()
    await db.commit()
    
    stmt = select(ClassGroup).options(selectinload(ClassGroup.schedules)).where(ClassGroup.id == db_group.id)
    result = await db.execute(stmt)
    db_group = result.scalar_one()
    
    return db_group

async def generate_lessons(db: AsyncSession, group_id: uuid.UUID, request: LessonGenerateRequest) -> List[Lesson]:
    # 1. Fetch group and schedules
    stmt = select(ClassGroup).options(selectinload(ClassGroup.schedules)).where(ClassGroup.id == group_id)
    result = await db.execute(stmt)
    group = result.scalar_one_or_none()
    
    if not group or not group.schedules:
        return []
        
    # 2. Find existing lessons in date range to avoid duplicates
    existing_stmt = select(Lesson).where(
        Lesson.class_group_id == group_id,
        Lesson.date >= request.start_date,
        Lesson.date <= request.end_date
    )
    existing_result = await db.execute(existing_stmt)
    existing_dates = { (l.date, l.start_time) for l in existing_result.scalars().all() }
    
    # 3. Generate new lessons
    new_lessons = []
    current_date = request.start_date
    while current_date <= request.end_date:
        weekday = current_date.weekday() # 0 = Monday, 6 = Sunday
        for sched in group.schedules:
            if sched.day_of_week == weekday:
                if (current_date, sched.start_time) not in existing_dates:
                    new_lesson = Lesson(
                        class_group_id=group.id,
                        date=current_date,
                        start_time=sched.start_time,
                        end_time=sched.end_time,
                        location=group.location,
                        instructor_name=group.instructor_name
                    )
                    db.add(new_lesson)
                    new_lessons.append(new_lesson)
        current_date += timedelta(days=1)
        
    if new_lessons:
        await db.flush()
        # Since we just inserted them and need to return them, 
        # flush is usually enough. If we really need them refreshed:
        # Actually they are already in the session with populated IDs if using UUID with default=uuid.uuid4
        # We don't even need to refresh because ID is generated client side or flush populates it.
        # So we can just return new_lessons directly.
            
    return new_lessons

async def get_class_groups(db: AsyncSession) -> List[ClassGroup]:
    stmt = select(ClassGroup).options(selectinload(ClassGroup.schedules))
    result = await db.execute(stmt)
    return list(result.unique().scalars().all())

async def get_lessons(db: AsyncSession) -> List[Lesson]:
    stmt = select(Lesson)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_class_group(db: AsyncSession, group_id: uuid.UUID) -> ClassGroup:
    stmt = (
        select(ClassGroup)
        .where(ClassGroup.id == group_id)
        .options(
            selectinload(ClassGroup.schedules),
            selectinload(ClassGroup.lessons),
        )
    )
    result = await db.execute(stmt)
    group = result.unique().scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class group not found")
    return group


async def update_class_group(db: AsyncSession, group_id: uuid.UUID, payload) -> ClassGroup:
    group = await get_class_group(db, group_id)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)
    await db.flush()
    return group


async def delete_class_group(db: AsyncSession, group_id: uuid.UUID) -> None:
    group = await get_class_group(db, group_id)
    await db.delete(group)
    await db.flush()


async def get_lesson(db: AsyncSession, lesson_id: uuid.UUID) -> Lesson:
    stmt = (
        select(Lesson)
        .where(Lesson.id == lesson_id)
        .options(
            selectinload(Lesson.class_group).selectinload(ClassGroup.schedules),
            selectinload(Lesson.attendances),
        )
    )
    result = await db.execute(stmt)
    lesson = result.unique().scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return lesson


async def get_lesson_attendance(db: AsyncSession, lesson_id: uuid.UUID) -> list[dict]:
    stmt = (
        select(AttendanceRecord, Student.name)
        .join(Student, AttendanceRecord.student_id == Student.id)
        .where(AttendanceRecord.lesson_id == lesson_id)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "id": record.id, "lesson_id": record.lesson_id,
            "student_id": record.student_id, "student_name": student_name,
            "present": record.present, "checked_in_at": record.checked_in_at,
        }
        for record, student_name in rows
    ]


async def batch_save_attendance(db: AsyncSession, lesson_id: uuid.UUID, records: list[dict]) -> list[dict]:
    lesson_stmt = select(Lesson).where(Lesson.id == lesson_id)
    lesson_result = await db.execute(lesson_stmt)
    if not lesson_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    for item in records:
        stmt = select(AttendanceRecord).where(
            AttendanceRecord.lesson_id == lesson_id,
            AttendanceRecord.student_id == item["student_id"],
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            existing.present = item["present"]
            existing.checked_in_at = datetime.now(timezone.utc) if item["present"] else None
        else:
            record = AttendanceRecord(
                lesson_id=lesson_id, student_id=item["student_id"],
                present=item["present"],
                checked_in_at=datetime.now(timezone.utc) if item["present"] else None,
            )
            db.add(record)
    await db.flush()
    return await get_lesson_attendance(db, lesson_id)


async def toggle_attendance(db: AsyncSession, record_id: uuid.UUID, present: bool) -> AttendanceRecord:
    stmt = select(AttendanceRecord).where(AttendanceRecord.id == record_id)
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")
    record.present = present
    record.checked_in_at = datetime.now(timezone.utc) if present else None
    await db.flush()
    return record
