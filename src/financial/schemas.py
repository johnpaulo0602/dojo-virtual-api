import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

class FinancialTransactionBase(BaseModel):
    type: str
    category: str
    description: str
    amount: Decimal
    date: date
    status: str = "pendente"
    paid_by: Optional[str] = Field(alias="paidBy", default=None)
    recurrence: str = "unico"
    installments: Optional[int] = None
    current_installment: Optional[int] = Field(alias="currentInstallment", default=None)

    model_config = ConfigDict(populate_by_name=True)

class FinancialTransactionCreate(FinancialTransactionBase):
    pass

class FinancialTransactionUpdate(BaseModel):
    type: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    date: Optional[date] = None
    status: Optional[str] = None
    paid_by: Optional[str] = None
    recurrence: Optional[str] = None
    installments: Optional[int] = None
    current_installment: Optional[int] = None

class FinancialTransactionResponse(FinancialTransactionBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class DonorBase(BaseModel):
    name: str
    email: str
    phone: str
    whatsapp: Optional[str] = None
    type: str
    document: str
    address: Optional[str] = None
    notes: Optional[str] = None

class DonorCreate(DonorBase):
    pass

class DonorResponse(DonorBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class DonationCreate(BaseModel):
    amount: Decimal
    date: date
    method: str
    description: str

class DonationResponse(DonationCreate):
    id: uuid.UUID
    donor_id: uuid.UUID = Field(alias="donorId")
    transaction_id: uuid.UUID = Field(alias="transactionId")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class DonorUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    type: str | None = None
    document: str | None = None
    address: str | None = None
    notes: str | None = None

class DonorDetailResponse(DonorResponse):
    donations: list[DonationResponse] = []
    total_donated: Decimal = Decimal("0")
