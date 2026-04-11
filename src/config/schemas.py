from pydantic import BaseModel

class FinancialCategory(BaseModel):
    id: str
    name: str
    type: str
    description: str = ""

class CategoriesPayload(BaseModel):
    categories: list[FinancialCategory]
