from pydantic import BaseModel

class FinancialCategory(BaseModel):
    id: str
    name: str
    type: str
    description: str = ""

class CategoriesPayload(BaseModel):
    categories: list[FinancialCategory]

class UserPreferences(BaseModel):
    notify_new_student: bool = True
    notify_attendance: bool = True
    notify_financial: bool = True
    notify_belt_promotion: bool = True

class OrganizationSettings(BaseModel):
    project_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    description: str = ""
    cnpj: str = ""
    socials: list[dict] = []
    managers: list[dict] = []
    default_belt: str = "branca"
    max_students_per_class: int = 25
    attendance_threshold: int = 75
    default_contribution: str = "0"
