# api/src/academic/services.py
from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from fastapi import HTTPException, status

from src.academic.models import Student, Guardian, StudentSchoolInfo, StudentHealthProfile, School
from src.academic.schemas import StudentOnboarding

async def get_students(db: AsyncSession) -> List[Student]:
    stmt = select(Student)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_schools(db: AsyncSession) -> List[School]:
    stmt = select(School)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def create_school(db: AsyncSession, payload) -> School:
    school = School(**payload.model_dump())
    db.add(school)
    await db.flush()
    return school

async def get_school(db: AsyncSession, school_id: uuid.UUID) -> School:
    stmt = select(School).where(School.id == school_id)
    result = await db.execute(stmt)
    school = result.scalar_one_or_none()
    if not school:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found")
    return school

async def update_school(db: AsyncSession, school_id: uuid.UUID, payload) -> School:
    school = await get_school(db, school_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(school, field, value)
    await db.flush()
    return school

async def delete_school(db: AsyncSession, school_id: uuid.UUID) -> None:
    school = await get_school(db, school_id)
    await db.delete(school)
    await db.flush()

async def create_student_onboarding(db: AsyncSession, payload: StudentOnboarding) -> Student:
    # Use nested dictionary mapping
    student_data = payload.model_dump(exclude={"guardians", "school_info", "health"})
    
    db_student = Student(**student_data)
    db.add(db_student)
    await db.flush() # get ID without committing
    
    if payload.guardians:
        for g_data in payload.guardians:
            db_guardian = Guardian(student_id=db_student.id, **g_data.model_dump())
            db.add(db_guardian)
            
    if payload.school_info:
        db_school_info = StudentSchoolInfo(student_id=db_student.id, **payload.school_info.model_dump())
        db.add(db_school_info)
        
    if payload.health:
        db_health = StudentHealthProfile(student_id=db_student.id, **payload.health.model_dump())
        db.add(db_health)

    student_id = db_student.id
    await db.commit()
    
    stmt = select(Student).where(Student.id == student_id).options(
        selectinload(Student.guardians),
        selectinload(Student.school_info),
        selectinload(Student.health_profile)
    )
    result = await db.execute(stmt)
    return result.scalar_one()

async def get_student(db: AsyncSession, student_id: uuid.UUID) -> Student:
    stmt = (
        select(Student)
        .where(Student.id == student_id)
        .options(
            selectinload(Student.guardians),
            selectinload(Student.school_info),
            selectinload(Student.health_profile),
        )
    )
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student
