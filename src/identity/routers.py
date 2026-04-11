from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.identity.schemas import UserCreate, UserResponse, Token, RefreshTokenRequest
from src.identity.services import register_user, authenticate_user, create_user_session, refresh_user_session, revoke_session, get_users
from src.identity.dependencies import get_current_user
from src.identity.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await register_user(db, payload)
    await db.commit()
    return user

@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(get_db)]):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = await create_user_session(db, user)
    await db.commit()
    return token

@router.post("/refresh", response_model=Token)
async def refresh_token(payload: RefreshTokenRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    token = await refresh_user_session(db, payload.refresh_token)
    await db.commit()
    return token

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshTokenRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    await revoke_session(db, payload.refresh_token)
    await db.commit()

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


users_router = APIRouter(prefix="/api/v1/users", tags=["users"])

@users_router.get("", response_model=list[UserResponse])
async def list_users(
    role: Annotated[str | None, Query(description="Comma-separated roles")] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    return await get_users(db, role)