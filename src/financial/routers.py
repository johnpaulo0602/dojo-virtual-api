import uuid
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from src.core.database import get_db
from src.financial.schemas import (
    DonationCreate, DonationResponse,
    FinancialTransactionCreate, FinancialTransactionUpdate, FinancialTransactionResponse,
    DonorCreate, DonorUpdate, DonorResponse, DonorDetailResponse,
)
from src.financial.services import (
    create_donation, get_financial_transactions, get_donors,
    create_financial_transaction, get_financial_transaction,
    update_financial_transaction, delete_financial_transaction,
    create_donor, get_donor, update_donor, delete_donor,
)
from src.identity.dependencies import get_current_user, RequireRole
from src.identity.models import User

_admin_only = RequireRole(["admin"])

router = APIRouter(prefix="/api/v1", tags=["financial"])

@router.post("/donors/{donor_id}/donations", response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
async def make_donation(
    donor_id: uuid.UUID,
    payload: DonationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    donation = await create_donation(db, donor_id, payload)
    await db.commit()
    return donation

@router.get("/financial-transactions", response_model=List[FinancialTransactionResponse])
async def list_transactions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    return await get_financial_transactions(db)

@router.post("/financial-transactions", response_model=FinancialTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: FinancialTransactionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    tx = await create_financial_transaction(db, payload)
    await db.commit()
    return tx

@router.get("/financial-transactions/{tx_id}", response_model=FinancialTransactionResponse)
async def read_transaction(
    tx_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    return await get_financial_transaction(db, tx_id)

@router.patch("/financial-transactions/{tx_id}", response_model=FinancialTransactionResponse)
async def patch_transaction(
    tx_id: Annotated[uuid.UUID, Path()],
    payload: FinancialTransactionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    tx = await update_financial_transaction(db, tx_id, payload)
    await db.commit()
    return tx

@router.delete("/financial-transactions/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_transaction(
    tx_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    await delete_financial_transaction(db, tx_id)
    await db.commit()

@router.get("/donors", response_model=List[DonorResponse])
async def list_donors(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    return await get_donors(db)

@router.post("/donors", response_model=DonorResponse, status_code=status.HTTP_201_CREATED)
async def create_new_donor(
    payload: DonorCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    donor = await create_donor(db, payload)
    await db.commit()
    return donor

@router.get("/donors/{donor_id}", response_model=DonorDetailResponse)
async def read_donor(
    donor_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    from decimal import Decimal as _Decimal
    donor = await get_donor(db, donor_id)
    if donor.donations:
        raw_total = sum(d.amount for d in donor.donations)
        # Strip trailing zeros but keep at least one decimal place (500.00 -> 500.0)
        normalized = raw_total.normalize()
        if normalized == normalized.to_integral_value():
            total = normalized.quantize(_Decimal("0.0"))
        else:
            total = normalized
    else:
        total = _Decimal("0")
    return {
        **{c.key: getattr(donor, c.key) for c in donor.__table__.columns},
        "donations": donor.donations,
        "total_donated": total,
    }

@router.patch("/donors/{donor_id}", response_model=DonorResponse)
async def patch_donor(
    donor_id: Annotated[uuid.UUID, Path()],
    payload: DonorUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    donor = await update_donor(db, donor_id, payload)
    await db.commit()
    return donor

@router.delete("/donors/{donor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_donor(
    donor_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(_admin_only)],
):
    await delete_donor(db, donor_id)
    await db.commit()
