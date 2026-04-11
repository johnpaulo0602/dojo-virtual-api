from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base

class Config(Base):
    __tablename__ = "config"
    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
