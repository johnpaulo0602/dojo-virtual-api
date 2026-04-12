from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.models import Config

DEFAULT_CATEGORIES = [
    {"id": "c1", "name": "Doações", "type": "receita", "description": "Doações de pessoas físicas e jurídicas"},
    {"id": "c2", "name": "Patrocínio", "type": "receita", "description": "Patrocínios de empresas parceiras"},
    {"id": "c3", "name": "Eventos", "type": "receita", "description": "Receita de eventos e competições"},
    {"id": "c4", "name": "Venda de Materiais", "type": "receita", "description": "Venda de kimonos e equipamentos"},
    {"id": "c5", "name": "Material Esportivo", "type": "despesa", "description": "Compra de kimonos, faixas e equipamentos"},
    {"id": "c6", "name": "Transporte", "type": "despesa", "description": "Transporte para competições e eventos"},
    {"id": "c7", "name": "Alimentação", "type": "despesa", "description": "Lanches e refeições para alunos"},
    {"id": "c8", "name": "Infraestrutura", "type": "despesa", "description": "Manutenção do espaço e equipamentos"},
    {"id": "c9", "name": "Salários", "type": "despesa", "description": "Pagamento de instrutores e monitores"},
]

async def get_categories(db: AsyncSession) -> list[dict]:
    stmt = select(Config).where(Config.key == "financial_categories")
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if not config:
        return DEFAULT_CATEGORIES
    return config.value.get("categories", [])

async def save_categories(db: AsyncSession, categories: list[dict]) -> list[dict]:
    stmt = select(Config).where(Config.key == "financial_categories")
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if config:
        config.value = {"categories": categories}
    else:
        config = Config(key="financial_categories", value={"categories": categories})
        db.add(config)
    await db.flush()
    return categories

DEFAULT_USER_PREFS = {
    "notify_new_student": True,
    "notify_attendance": True,
    "notify_financial": True,
    "notify_belt_promotion": True,
}

async def get_user_prefs(db: AsyncSession, user_id: str) -> dict:
    key = f"user_prefs_{user_id}"
    stmt = select(Config).where(Config.key == key)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if not config:
        return DEFAULT_USER_PREFS
    return config.value

async def save_user_prefs(db: AsyncSession, user_id: str, prefs: dict) -> dict:
    key = f"user_prefs_{user_id}"
    stmt = select(Config).where(Config.key == key)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if config:
        config.value = prefs
    else:
        config = Config(key=key, value=prefs)
        db.add(config)
    await db.flush()
    return prefs

DEFAULT_ORG_SETTINGS = {
    "project_name": "", "email": "", "phone": "", "address": "",
    "description": "", "cnpj": "", "socials": [], "managers": [],
    "default_belt": "branca", "max_students_per_class": 25,
    "attendance_threshold": 75, "default_contribution": "0",
}

async def get_organization(db: AsyncSession) -> dict:
    stmt = select(Config).where(Config.key == "organization")
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if not config:
        return DEFAULT_ORG_SETTINGS
    return {**DEFAULT_ORG_SETTINGS, **config.value}

async def save_organization(db: AsyncSession, settings: dict) -> dict:
    stmt = select(Config).where(Config.key == "organization")
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if config:
        config.value = settings
    else:
        config = Config(key="organization", value=settings)
        db.add(config)
    await db.flush()
    return settings
