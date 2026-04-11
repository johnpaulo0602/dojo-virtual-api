import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.config import settings
from src.core.database import async_sessionmaker, engine
from src.identity.models import User
from src.identity.schemas import UserCreate
from src.identity.services import register_user

logger = logging.getLogger("uvicorn.error")

async def create_initial_admin() -> None:
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        logger.info("ADMIN_EMAIL ou ADMIN_PASSWORD não configurados no .env. Pulando criação automática de admin.")
        return

    async with async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)() as session:
        stmt = select(User).where(User.email == settings.ADMIN_EMAIL)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            logger.info(f"Criando administrador inicial: {settings.ADMIN_EMAIL}")
            user_in = UserCreate(
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                role="admin",
            )
            await register_user(session, user_in)
            await session.commit()
            logger.info("Administrador inicial criado com sucesso.")
        else:
            logger.info(f"Administrador {settings.ADMIN_EMAIL} já existe no banco de dados.")
