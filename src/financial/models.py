# api/src/financial/models.py
import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, Integer, Date, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base

class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String, nullable=False) # receita, despesa
    category: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pendente") # pago, pendente, cancelado
    paid_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    recurrence: Mapped[str] = mapped_column(String, default="unico")
    installments: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_installment: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

class Donor(Base):
    __tablename__ = "donors"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    whatsapp: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=False) # pessoa_fisica, pessoa_juridica
    document: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    donations: Mapped[List["Donation"]] = relationship(back_populates="donor", cascade="all, delete-orphan")

class Donation(Base):
    __tablename__ = "donations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    donor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("donors.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    method: Mapped[str] = mapped_column(String, nullable=False) # pix, transferencia, dinheiro, cartao
    description: Mapped[str] = mapped_column(String, nullable=False)
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("financial_transactions.id", ondelete="RESTRICT"), unique=True, nullable=False)

    donor: Mapped["Donor"] = relationship(back_populates="donations")
