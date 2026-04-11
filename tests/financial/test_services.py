import pytest
import uuid
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.financial.services import create_donation
from src.financial.schemas import DonationCreate
from src.financial.models import Donor, FinancialTransaction

@pytest.mark.asyncio
async def test_create_donation_creates_transaction(get_db_session: AsyncSession):
    # Create donor
    donor = Donor(name="Test", email="test@test.com", phone="123", type="pessoa_fisica", document="123")
    get_db_session.add(donor)
    await get_db_session.flush()

    payload = DonationCreate(
        amount=Decimal("100.50"),
        date=date(2026, 4, 15),
        method="pix",
        description="Donation April"
    )

    donation = await create_donation(get_db_session, donor.id, payload)
    
    assert donation.id is not None
    assert donation.amount == Decimal("100.50")
    
    # Verify transaction was created
    stmt = select(FinancialTransaction).where(FinancialTransaction.id == donation.transaction_id)
    res = await get_db_session.execute(stmt)
    transaction = res.scalar_one_or_none()
    
    assert transaction is not None
    assert transaction.type == "receita"
    assert transaction.category == "doacao"
    assert transaction.amount == Decimal("100.50")
    assert transaction.status == "pago"
