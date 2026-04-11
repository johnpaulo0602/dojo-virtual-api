from typing import Annotated, List
import uuid
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.academic.schemas import StudentOnboarding, StudentResponse, SchoolResponse, StudentDetailResponse, SchoolCreate, SchoolUpdate
from src.academic.services import create_student_onboarding, get_students, get_schools, get_student, create_school, update_school, delete_school
from src.identity.dependencies import get_current_user
from src.identity.models import User

router = APIRouter(prefix="/api/v1/students", tags=["students"])

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
    db: Annotated[AsyncSession, Depends(get_db)]
):
    student = await create_student_onboarding(db, payload)
    return student

@router.get("/{student_id}", response_model=StudentDetailResponse)
async def read_student(
    student_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await get_student(db, student_id)
