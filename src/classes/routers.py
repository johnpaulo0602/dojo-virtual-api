import uuid
from typing import List, Annotated
from fastapi import APIRouter, Depends, Path, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.identity.dependencies import get_current_user
from src.identity.models import User
from src.classes.schemas import (
    ClassGroupCreate, ClassGroupResponse, ClassGroupUpdate, ClassGroupDetailResponse,
    LessonGenerateRequest, LessonResponse, LessonDetailResponse,
    AttendanceRecordResponse, AttendanceBatchUpdate, AttendanceUpdate,
)
from src.classes.services import (
    create_class_group, generate_lessons, get_class_groups, get_lessons,
    get_class_group, update_class_group, delete_class_group, get_lesson,
    get_lesson_attendance, batch_save_attendance, toggle_attendance,
)
from src.academic.models import Student

router = APIRouter(prefix="/api/v1/class-groups", tags=["classes"])

# 1. GET / — list groups
@router.get("", response_model=List[ClassGroupResponse])
async def list_class_groups(db: Annotated[AsyncSession, Depends(get_db)]):
    return await get_class_groups(db)

# 2. GET /lessons — list all lessons
@router.get("/lessons", response_model=List[LessonResponse])
async def list_lessons(db: Annotated[AsyncSession, Depends(get_db)]):
    return await get_lessons(db)

# 3. GET /lessons/{lesson_id}/attendance — list attendance for a lesson
@router.get("/lessons/{lesson_id}/attendance", response_model=list[AttendanceRecordResponse])
async def read_lesson_attendance(
    lesson_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await get_lesson_attendance(db, lesson_id)

# 4. POST /lessons/{lesson_id}/attendance — batch save attendance
@router.post("/lessons/{lesson_id}/attendance", response_model=list[AttendanceRecordResponse])
async def save_lesson_attendance(
    lesson_id: Annotated[uuid.UUID, Path()],
    payload: AttendanceBatchUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    records = [{"student_id": r.student_id, "present": r.present} for r in payload.records]
    result = await batch_save_attendance(db, lesson_id, records)
    await db.commit()
    return result

# 5. GET /lessons/{lesson_id} — lesson detail (must be BEFORE /{group_id})
@router.get("/lessons/{lesson_id}", response_model=LessonDetailResponse)
async def read_lesson(
    lesson_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    lesson = await get_lesson(db, lesson_id)
    attendance_data = []
    for record in lesson.attendances:
        attendance_data.append({
            "id": record.id,
            "lesson_id": record.lesson_id,
            "student_id": record.student_id,
            "student_name": "",
            "present": record.present,
            "checked_in_at": record.checked_in_at,
        })
    return {
        **{c.key: getattr(lesson, c.key) for c in lesson.__table__.columns},
        "class_group": lesson.class_group,
        "attendance": attendance_data,
    }

# 4. POST / — create group
@router.post("", response_model=ClassGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(payload: ClassGroupCreate, db: AsyncSession = Depends(get_db)):
    return await create_class_group(db, payload)

# 6. POST /{group_id}/lessons/generate — generate lessons
@router.post("/{group_id}/lessons/generate", response_model=List[LessonResponse], status_code=status.HTTP_201_CREATED)
async def generate_group_lessons(group_id: uuid.UUID, payload: LessonGenerateRequest, db: AsyncSession = Depends(get_db)):
    lessons = await generate_lessons(db, group_id, payload)
    return lessons

# 7. PATCH /attendance/{record_id} — toggle individual attendance
@router.patch("/attendance/{record_id}", response_model=AttendanceRecordResponse)
async def patch_attendance(
    record_id: Annotated[uuid.UUID, Path()],
    payload: AttendanceUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    record = await toggle_attendance(db, record_id, payload.present)
    await db.commit()
    student_stmt = select(Student.name).where(Student.id == record.student_id)
    student_result = await db.execute(student_stmt)
    student_name = student_result.scalar_one_or_none() or ""
    return {
        "id": record.id, "lesson_id": record.lesson_id,
        "student_id": record.student_id, "student_name": student_name,
        "present": record.present, "checked_in_at": record.checked_in_at,
    }

# 8. GET /{group_id} — group detail
@router.get("/{group_id}", response_model=ClassGroupDetailResponse)
async def read_class_group(
    group_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    group = await get_class_group(db, group_id)
    return {
        **{c.key: getattr(group, c.key) for c in group.__table__.columns},
        "schedules": group.schedules,
        "lessons_count": len(group.lessons) if group.lessons else 0,
        "enrolled_count": 0,
    }

# 7. PATCH /{group_id} — update group
@router.patch("/{group_id}", response_model=ClassGroupResponse)
async def patch_class_group(
    group_id: Annotated[uuid.UUID, Path()],
    payload: ClassGroupUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    group = await update_class_group(db, group_id, payload)
    await db.commit()
    return group

# 8. DELETE /{group_id} — delete group
@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_class_group(
    group_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await delete_class_group(db, group_id)
    await db.commit()
