from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.identity.dependencies import get_current_user, RequireRole
from src.identity.models import User
from src.dashboard.schemas import DashboardSummary
from src.dashboard.services import get_dashboard_summary

_dashboard_roles = RequireRole(["admin", "instrutor", "monitor"])

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummary)
async def read_dashboard_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_dashboard_roles)],
):
    return await get_dashboard_summary(db)
