from datetime import date
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.academic.models import Student
from src.classes.models import ClassGroup, Lesson
from src.financial.models import FinancialTransaction, Donor

async def get_dashboard_summary(db: AsyncSession) -> dict:
    today = date.today()
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1)
    else:
        month_end = today.replace(month=today.month + 1, day=1)

    total_students = (await db.execute(select(func.count(Student.id)))).scalar() or 0
    active_students = (await db.execute(select(func.count(Student.id)).where(Student.status == "ativo"))).scalar() or 0
    total_class_groups = (await db.execute(select(func.count(ClassGroup.id)))).scalar() or 0
    active_class_groups = (await db.execute(select(func.count(ClassGroup.id)).where(ClassGroup.status == "ativa"))).scalar() or 0
    total_lessons_month = (await db.execute(select(func.count(Lesson.id)).where(Lesson.date >= month_start, Lesson.date < month_end))).scalar() or 0
    monthly_revenue = (await db.execute(select(func.coalesce(func.sum(FinancialTransaction.amount), 0)).where(
        FinancialTransaction.type == "receita", FinancialTransaction.date >= month_start, FinancialTransaction.date < month_end,
    ))).scalar() or Decimal("0")
    monthly_expenses = (await db.execute(select(func.coalesce(func.sum(FinancialTransaction.amount), 0)).where(
        FinancialTransaction.type == "despesa", FinancialTransaction.date >= month_start, FinancialTransaction.date < month_end,
    ))).scalar() or Decimal("0")
    total_donors = (await db.execute(select(func.count(Donor.id)))).scalar() or 0

    return {
        "total_students": total_students, "active_students": active_students,
        "total_class_groups": total_class_groups, "active_class_groups": active_class_groups,
        "total_lessons_month": total_lessons_month,
        "monthly_revenue": monthly_revenue, "monthly_expenses": monthly_expenses,
        "total_donors": total_donors,
    }
