from decimal import Decimal
from pydantic import BaseModel, field_serializer

class DashboardSummary(BaseModel):
    total_students: int
    active_students: int
    total_class_groups: int
    active_class_groups: int
    total_lessons_month: int
    monthly_revenue: Decimal
    monthly_expenses: Decimal
    total_donors: int

    @field_serializer("monthly_revenue", "monthly_expenses")
    def serialize_decimal(self, value: Decimal) -> str:
        # Format as plain decimal, then strip trailing fractional zeros
        s = format(value, "f")
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return s
