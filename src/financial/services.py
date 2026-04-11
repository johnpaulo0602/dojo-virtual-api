import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from src.financial.models import FinancialTransaction, Donor, Donation
from src.financial.schemas import DonationCreate

async def create_donation(db: AsyncSession, donor_id: uuid.UUID, payload: DonationCreate) -> Donation:
    # 1. Create the underlying financial transaction
    transaction = FinancialTransaction(
        type="receita",
        category="doacao",
        description=payload.description,
        amount=payload.amount,
        date=payload.date,
        status="pago", # Donations are always confirmed funds
        paid_by="Doador"
    )
    db.add(transaction)
    
    try:
        await db.flush() # flush to get the transaction.id
        
        # 2. Create the specific donation record linked to the transaction and donor
        donation = Donation(
            donor_id=donor_id,
            amount=payload.amount,
            date=payload.date,
            method=payload.method,
            description=payload.description,
            transaction_id=transaction.id
        )
        db.add(donation)
        
        await db.flush()
        return donation
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Database integrity error when saving donation.")

async def get_financial_transactions(db: AsyncSession) -> List[FinancialTransaction]:
    stmt = select(FinancialTransaction).order_by(FinancialTransaction.date.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_donors(db: AsyncSession) -> List[Donor]:
    stmt = select(Donor)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def create_financial_transaction(db: AsyncSession, payload) -> FinancialTransaction:
    tx = FinancialTransaction(**payload.model_dump())
    db.add(tx)
    await db.flush()
    return tx

async def get_financial_transaction(db: AsyncSession, tx_id: uuid.UUID) -> FinancialTransaction:
    stmt = select(FinancialTransaction).where(FinancialTransaction.id == tx_id)
    result = await db.execute(stmt)
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return tx

async def update_financial_transaction(db: AsyncSession, tx_id: uuid.UUID, payload) -> FinancialTransaction:
    tx = await get_financial_transaction(db, tx_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tx, field, value)
    await db.flush()
    return tx

async def delete_financial_transaction(db: AsyncSession, tx_id: uuid.UUID) -> None:
    tx = await get_financial_transaction(db, tx_id)
    await db.delete(tx)
    await db.flush()

async def create_donor(db: AsyncSession, payload) -> Donor:
    donor = Donor(**payload.model_dump())
    db.add(donor)
    await db.flush()
    return donor

async def get_donor(db: AsyncSession, donor_id: uuid.UUID) -> Donor:
    stmt = (
        select(Donor).where(Donor.id == donor_id)
        .options(selectinload(Donor.donations))
    )
    result = await db.execute(stmt)
    donor = result.unique().scalar_one_or_none()
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")
    return donor

async def update_donor(db: AsyncSession, donor_id: uuid.UUID, payload) -> Donor:
    donor = await get_donor(db, donor_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(donor, field, value)
    await db.flush()
    return donor

async def delete_donor(db: AsyncSession, donor_id: uuid.UUID) -> None:
    donor = await get_donor(db, donor_id)
    await db.delete(donor)
    await db.flush()
