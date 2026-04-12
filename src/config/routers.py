from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.identity.dependencies import get_current_user, RequireRole
from src.identity.models import User
from src.config.schemas import CategoriesPayload, UserPreferences, OrganizationSettings
from src.config.services import get_categories, save_categories, get_user_prefs, save_user_prefs, get_organization, save_organization

_admin_only = RequireRole(["admin"])

router = APIRouter(prefix="/api/v1/config", tags=["config"])

@router.get("/categories", response_model=CategoriesPayload)
async def read_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    cats = await get_categories(db)
    return {"categories": cats}

@router.put("/categories", response_model=CategoriesPayload)
async def replace_categories(
    payload: CategoriesPayload,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    cats = await save_categories(db, [c.model_dump() for c in payload.categories])
    await db.commit()
    return {"categories": cats}

@router.get("/user_prefs", response_model=UserPreferences)
async def read_user_prefs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    return await get_user_prefs(db, str(current_user.id))

@router.put("/user_prefs", response_model=UserPreferences)
async def replace_user_prefs(
    payload: UserPreferences,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    prefs = await save_user_prefs(db, str(current_user.id), payload.model_dump())
    await db.commit()
    return prefs

@router.get("/organization", response_model=OrganizationSettings)
async def read_organization(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    return await get_organization(db)

@router.put("/organization", response_model=OrganizationSettings)
async def replace_organization(
    payload: OrganizationSettings,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    settings = await save_organization(db, payload.model_dump())
    await db.commit()
    return settings
