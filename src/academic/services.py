# api/src/academic/services.py
import uuid
from typing import List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from fastapi import HTTPException, status

from src.academic.models import (
    Student, Guardian, StudentSchoolInfo, StudentHealthProfile, School,
    EmergencyContact, BeltPromotion, InstructorFeedback, StudentContribution, StudentDocument,
)
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


def _generate_matricula() -> str:
    import random
    return f"MAT{random.randint(10000, 99999)}"


async def create_student_onboarding(db: AsyncSession, payload: StudentOnboarding) -> Student:
    data = payload.model_dump(exclude={"class_group_id"})
    data["matricula"] = _generate_matricula()
    student = Student(**data)
    db.add(student)
    await db.flush()  # assigns student.id
    student_id = student.id
    await db.commit()
    stmt = select(Student).where(Student.id == student_id)
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
            selectinload(Student.emergency_contacts),
            selectinload(Student.promotions),
            selectinload(Student.feedbacks),
            selectinload(Student.contributions),
            selectinload(Student.documents),
        )
    )
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


async def update_student(db: AsyncSession, student_id: uuid.UUID, payload) -> Student:
    student = await get_student(db, student_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    await db.flush()
    return student


# --- Guardians ---

async def create_guardian(db: AsyncSession, student_id: uuid.UUID, payload) -> Guardian:
    guardian = Guardian(student_id=student_id, **payload.model_dump())
    db.add(guardian)
    await db.flush()
    return guardian


async def update_guardian(db: AsyncSession, guardian_id: uuid.UUID, payload) -> Guardian:
    stmt = select(Guardian).where(Guardian.id == guardian_id)
    result = await db.execute(stmt)
    guardian = result.scalar_one_or_none()
    if not guardian:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guardian not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(guardian, field, value)
    await db.flush()
    return guardian


async def delete_guardian(db: AsyncSession, guardian_id: uuid.UUID) -> None:
    stmt = select(Guardian).where(Guardian.id == guardian_id)
    result = await db.execute(stmt)
    guardian = result.scalar_one_or_none()
    if not guardian:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guardian not found")
    await db.delete(guardian)
    await db.flush()


# --- Emergency Contacts ---

async def get_emergency_contacts(db: AsyncSession, student_id: uuid.UUID) -> List[EmergencyContact]:
    stmt = select(EmergencyContact).where(EmergencyContact.student_id == student_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_emergency_contact(db: AsyncSession, student_id: uuid.UUID, payload) -> EmergencyContact:
    contact = EmergencyContact(student_id=student_id, **payload.model_dump())
    db.add(contact)
    await db.flush()
    return contact


async def update_emergency_contact(db: AsyncSession, contact_id: uuid.UUID, payload) -> EmergencyContact:
    stmt = select(EmergencyContact).where(EmergencyContact.id == contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency contact not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    await db.flush()
    return contact


async def delete_emergency_contact(db: AsyncSession, contact_id: uuid.UUID) -> None:
    stmt = select(EmergencyContact).where(EmergencyContact.id == contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency contact not found")
    await db.delete(contact)
    await db.flush()


# --- Belt Promotions ---

async def get_promotions(db: AsyncSession, student_id: uuid.UUID) -> List[BeltPromotion]:
    stmt = select(BeltPromotion).where(BeltPromotion.student_id == student_id).order_by(BeltPromotion.date.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_promotion(db: AsyncSession, student_id: uuid.UUID, payload) -> BeltPromotion:
    promo = BeltPromotion(student_id=student_id, **payload.model_dump())
    db.add(promo)
    await db.flush()
    return promo


# --- Instructor Feedbacks ---

async def get_feedbacks(db: AsyncSession, student_id: uuid.UUID) -> List[InstructorFeedback]:
    stmt = select(InstructorFeedback).where(InstructorFeedback.student_id == student_id).order_by(InstructorFeedback.date.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_feedback(db: AsyncSession, student_id: uuid.UUID, author_id: uuid.UUID, payload) -> InstructorFeedback:
    fb = InstructorFeedback(student_id=student_id, author_id=author_id, **payload.model_dump())
    db.add(fb)
    await db.flush()
    return fb


# --- Student Contributions ---

async def get_contributions(db: AsyncSession, student_id: uuid.UUID) -> List[StudentContribution]:
    stmt = select(StudentContribution).where(StudentContribution.student_id == student_id).order_by(StudentContribution.date.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_contribution(db: AsyncSession, student_id: uuid.UUID, payload) -> StudentContribution:
    contrib = StudentContribution(student_id=student_id, **payload.model_dump())
    db.add(contrib)
    await db.flush()
    return contrib


# --- Student Documents ---

async def get_documents(db: AsyncSession, student_id: uuid.UUID) -> List[StudentDocument]:
    stmt = select(StudentDocument).where(StudentDocument.student_id == student_id).order_by(StudentDocument.uploaded_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_document(db: AsyncSession, student_id: uuid.UUID, payload) -> StudentDocument:
    doc = StudentDocument(student_id=student_id, **payload.model_dump())
    db.add(doc)
    await db.flush()
    return doc


async def delete_document(db: AsyncSession, doc_id: uuid.UUID) -> None:
    stmt = select(StudentDocument).where(StudentDocument.id == doc_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    await db.delete(doc)
    await db.flush()
