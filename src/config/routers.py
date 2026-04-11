from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.identity.dependencies import get_current_user
from src.identity.models import User
from src.config.schemas import CategoriesPayload
from src.config.services import get_categories, save_categories

router = APIRouter(prefix="/api/v1/config", tags=["config"])

@router.get("/categories", response_model=CategoriesPayload)
async def read_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    cats = await get_categories(db)
    return {"categories": cats}

@router.put("/categories", response_model=CategoriesPayload)
async def replace_categories(
    payload: CategoriesPayload,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    cats = await save_categories(db, [c.model_dump() for c in payload.categories])
    await db.commit()
    return {"categories": cats}
