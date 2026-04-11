from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from src.core.config import settings
from src.identity.models import User, RefreshToken
from src.identity.schemas import UserCreate, Token

async def register_user(db: AsyncSession, payload: UserCreate) -> User:
    user = User(
        email=payload.email,
        name=payload.name,
        hashed_password=get_password_hash(payload.password),
        role=payload.role
    )
    db.add(user)
    try:
        await db.flush()
        return user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def create_user_session(db: AsyncSession, user: User) -> Token:
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token_str = create_refresh_token()
    
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    await db.flush()
    
    return Token(access_token=access_token, refresh_token=refresh_token_str)

async def refresh_user_session(db: AsyncSession, refresh_token: str) -> Token:
    stmt = select(RefreshToken).where(RefreshToken.token == refresh_token)
    result = await db.execute(stmt)
    db_token = result.scalar_one_or_none()
    
    if not db_token or db_token.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
        
    # Get user
    stmt_user = select(User).where(User.id == db_token.user_id)
    result_user = await db.execute(stmt_user)
    user = result_user.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    # Rotate token: delete old, create new
    await db.delete(db_token)
    
    return await create_user_session(db, user)

async def revoke_session(db: AsyncSession, refresh_token: str):
    stmt = select(RefreshToken).where(RefreshToken.token == refresh_token)
    result = await db.execute(stmt)
    db_token = result.scalar_one_or_none()

    if db_token:
        db_token.revoked_at = datetime.now(timezone.utc)
        await db.flush()

async def get_users(db: AsyncSession, role: str | None = None) -> list[User]:
    stmt = select(User)
    if role:
        roles = [r.strip() for r in role.split(",")]
        stmt = stmt.where(User.role.in_(roles))
    result = await db.execute(stmt)
    return list(result.scalars().all())
