# api/src/academic/routers.py
from typing import Annotated, List
import uuid
import os
import shutil
from fastapi import APIRouter, Depends, status, Path, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.identity.dependencies import get_current_user
from src.identity.models import User

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
from src.academic.schemas import (
    StudentOnboarding, StudentUpdate, StudentResponse, StudentDetailResponse,
    SchoolResponse, SchoolCreate, SchoolUpdate,
    EmergencyContactCreate, EmergencyContactResponse,
    BeltPromotionCreate, BeltPromotionResponse,
    InstructorFeedbackCreate, InstructorFeedbackResponse,
    StudentContributionCreate, StudentContributionResponse,
    StudentDocumentCreate, StudentDocumentResponse,
    GuardianCreate, GuardianResponse,
    SchoolInfoCreate, SchoolInfoResponse,
    HealthProfileCreate, HealthProfileResponse,
)
from src.academic.services import (
    get_students, get_schools, create_school, update_school, delete_school,
    create_student_onboarding, get_student, update_student,
    create_guardian, update_guardian, delete_guardian,
    get_emergency_contacts, create_emergency_contact, update_emergency_contact, delete_emergency_contact,
    get_promotions, create_promotion,
    get_feedbacks, create_feedback,
    get_contributions, create_contribution,
    get_documents, create_document, delete_document,
)
from sqlalchemy import select
from src.academic.models import Guardian

router = APIRouter(prefix="/api/v1/students", tags=["students"])

# --- Students ---

@router.get("", response_model=List[StudentResponse])
async def list_students(db: Annotated[AsyncSession, Depends(get_db)]):
    return await get_students(db)


@router.get("/schools", response_model=List[SchoolResponse])
async def list_schools(db: Annotated[AsyncSession, Depends(get_db)]):
    return await get_schools(db)


@router.post("/schools", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_new_school(
    payload: SchoolCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    school = await create_school(db, payload)
    await db.commit()
    return school


@router.patch("/schools/{school_id}", response_model=SchoolResponse)
async def patch_school(
    school_id: Annotated[uuid.UUID, Path()],
    payload: SchoolUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    school = await update_school(db, school_id, payload)
    await db.commit()
    return school


@router.delete("/schools/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_school(
    school_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await delete_school(db, school_id)
    await db.commit()


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def onboard_student(
    payload: StudentOnboarding,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await create_student_onboarding(db, payload)


@router.get("/{student_id}", response_model=StudentDetailResponse)
async def read_student(
    student_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await get_student(db, student_id)


@router.patch("/{student_id}", response_model=StudentResponse)
async def patch_student(
    student_id: Annotated[uuid.UUID, Path()],
    payload: StudentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    student = await update_student(db, student_id, payload)
    await db.commit()
    return student


# --- Guardians ---

@router.get("/{student_id}/guardians", response_model=List[GuardianResponse])
async def list_guardians(
    student_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    stmt = select(Guardian).where(Guardian.student_id == student_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/{student_id}/guardians", response_model=GuardianResponse, status_code=status.HTTP_201_CREATED)
async def add_guardian(
    student_id: Annotated[uuid.UUID, Path()],
    payload: GuardianCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    guardian = await create_guardian(db, student_id, payload)
    await db.commit()
    return guardian


@router.patch("/{student_id}/guardians/{guardian_id}", response_model=GuardianResponse)
async def patch_guardian(
    student_id: Annotated[uuid.UUID, Path()],
    guardian_id: Annotated[uuid.UUID, Path()],
    payload: GuardianCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    guardian = await update_guardian(db, guardian_id, payload)
    await db.commit()
    return guardian


@router.delete("/{student_id}/guardians/{guardian_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_guardian(
    student_id: Annotated[uuid.UUID, Path()],
    guardian_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await delete_guardian(db, guardian_id)
    await db.commit()


# --- Emergency Contacts ---

@router.get("/{student_id}/emergency-contacts", response_model=List[EmergencyContactResponse])
async def list_emergency_contacts(
    student_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await get_emergency_contacts(db, student_id)


@router.post("/{student_id}/emergency-contacts", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED)
async def add_emergency_contact(
    student_id: Annotated[uuid.UUID, Path()],
    payload: EmergencyContactCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    contact = await create_emergency_contact(db, student_id, payload)
    await db.commit()
    return contact


@router.patch("/{student_id}/emergency-contacts/{contact_id}", response_model=EmergencyContactResponse)
async def patch_emergency_contact(
    student_id: Annotated[uuid.UUID, Path()],
    contact_id: Annotated[uuid.UUID, Path()],
    payload: EmergencyContactCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    contact = await update_emergency_contact(db, contact_id, payload)
    await db.commit()
    return contact


@router.delete("/{student_id}/emergency-contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_emergency_contact(
    student_id: Annotated[uuid.UUID, Path()],
    contact_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await delete_emergency_contact(db, contact_id)
    await db.commit()


# --- Belt Promotions ---

@router.get("/{student_id}/promotions", response_model=List[BeltPromotionResponse])
async def list_promotions(
    student_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await get_promotions(db, student_id)


@router.post("/{student_id}/promotions", response_model=BeltPromotionResponse, status_code=status.HTTP_201_CREATED)
async def add_promotion(
    student_id: Annotated[uuid.UUID, Path()],
    payload: BeltPromotionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    promo = await create_promotion(db, student_id, payload)
    await db.commit()
    return promo


# --- Instructor Feedbacks ---

@router.get("/{student_id}/feedbacks", response_model=List[InstructorFeedbackResponse])
async def list_feedbacks(
    student_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await get_feedbacks(db, student_id)


@router.post("/{student_id}/feedbacks", response_model=InstructorFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def add_feedback(
    student_id: Annotated[uuid.UUID, Path()],
    payload: InstructorFeedbackCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    fb = await create_feedback(db, student_id, current_user.id, payload)
    await db.commit()
    return fb


# --- Student Contributions ---

@router.get("/{student_id}/contributions", response_model=List[StudentContributionResponse])
async def list_contributions(
    student_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await get_contributions(db, student_id)


@router.post("/{student_id}/contributions", response_model=StudentContributionResponse, status_code=status.HTTP_201_CREATED)
async def add_contribution(
    student_id: Annotated[uuid.UUID, Path()],
    payload: StudentContributionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    contrib = await create_contribution(db, student_id, payload)
    await db.commit()
    return contrib


# --- Student Documents ---

@router.get("/{student_id}/documents", response_model=List[StudentDocumentResponse])
async def list_documents(
    student_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await get_documents(db, student_id)


@router.post("/{student_id}/documents", response_model=StudentDocumentResponse, status_code=status.HTTP_201_CREATED)
async def add_document(
    student_id: Annotated[uuid.UUID, Path()],
    payload: StudentDocumentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    doc = await create_document(db, student_id, payload)
    await db.commit()
    return doc


@router.delete("/{student_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document(
    student_id: Annotated[uuid.UUID, Path()],
    doc_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await delete_document(db, doc_id)
    await db.commit()


@router.post("/{student_id}/upload")
async def upload_file(
    student_id: Annotated[uuid.UUID, Path()],
    file: UploadFile,
    current_user: Annotated[User, Depends(get_current_user)],
):
    ext = os.path.splitext(file.filename or "file")[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"url": f"/uploads/{filename}", "filename": file.filename}
