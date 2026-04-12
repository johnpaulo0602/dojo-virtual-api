import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from src.core.database import Base
from src.core.config import settings
from src.identity.models import User
from src.core.security import get_password_hash, create_access_token

# Import all models so Base.metadata knows about every table (needed for drop_all/create_all ordering)
import src.academic.models  # noqa: F401
import src.classes.models  # noqa: F401
import src.financial.models  # noqa: F401
import src.config.models  # noqa: F401

# Use a test database URL or rely on transactions
# For simplicity, we create tables and yield session

engine = create_async_engine(settings.DATABASE_URL, echo=False, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="function")
async def get_db_session() -> AsyncSession:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def auth_token(get_db_session: AsyncSession) -> str:
    user = User(
        email="testuser@test.com",
        name="Test User",
        hashed_password=get_password_hash("testpass"),
        role="admin",
    )
    get_db_session.add(user)
    await get_db_session.flush()
    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return token
