# api/src/academic/schemas.py
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class AddressSchema(BaseModel):
    cep: str
    street: str
    number: str
    complement: Optional[str] = None
    neighborhood: str
    city: str
    state: str


class StudentOnboarding(BaseModel):
    """Simplified wizard: personal data + address + jiu-jitsu only."""
    name: str
    cpf: str
    birth_date: date = Field(alias="birthDate")
    gender: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[AddressSchema] = None
    # Jiu-Jitsu
    belt_name: str = Field(alias="beltName")
    belt_degree: int = Field(alias="beltDegree", default=0)
    start_date: Optional[date] = Field(alias="startDate", default=None)
    class_group_id: Optional[uuid.UUID] = Field(alias="classGroupId", default=None)

    model_config = ConfigDict(populate_by_name=True)


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[AddressSchema] = None
    belt_name: Optional[str] = None
    belt_degree: Optional[int] = None
    status: Optional[str] = None
    profession: Optional[str] = None
    start_date: Optional[date] = None
    contributes: Optional[bool] = None
    contribution_amount: Optional[Decimal] = None


class StudentResponse(BaseModel):
    id: uuid.UUID
    name: str
    cpf: str
    matricula: str
    birth_date: date
    gender: str
    phone: Optional[str] = None
    email: Optional[str] = None
    belt_name: str
    belt_degree: int
    status: str
    profession: Optional[str] = None
    start_date: Optional[date] = None
    contributes: bool = False
    contribution_amount: Optional[Decimal] = None
    model_config = ConfigDict(from_attributes=True)


class SchoolResponse(BaseModel):
    id: uuid.UUID
    name: str
    address: str
    model_config = ConfigDict(from_attributes=True)


class SchoolCreate(BaseModel):
    name: str
    address: str


class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None


# Guardian schemas
class GuardianCreate(BaseModel):
    name: str
    cpf: str
    relationship_type: str = Field(alias="relationshipType")
    phone: str
    email: Optional[str] = None
    profession: Optional[str] = None
    is_primary: bool = Field(alias="isPrimary", default=False)
    model_config = ConfigDict(populate_by_name=True)


class GuardianResponse(BaseModel):
    id: uuid.UUID
    name: str
    cpf: str
    relationship_type: str
    phone: str
    email: Optional[str] = None
    profession: Optional[str] = None
    is_primary: bool
    model_config = ConfigDict(from_attributes=True)


# SchoolInfo schemas
class SchoolInfoCreate(BaseModel):
    school_id: uuid.UUID = Field(alias="schoolId")
    is_student: bool = Field(alias="isStudent", default=True)
    school_level: Optional[str] = Field(alias="schoolLevel", default=None)
    school_year: Optional[str] = Field(alias="schoolYear", default=None)
    school_shift: Optional[str] = Field(alias="schoolShift", default=None)
    model_config = ConfigDict(populate_by_name=True)


class SchoolInfoResponse(BaseModel):
    id: uuid.UUID
    school_id: uuid.UUID
    is_student: bool
    school_level: Optional[str] = None
    school_year: Optional[str] = None
    school_shift: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# HealthProfile schemas
class HealthProfileCreate(BaseModel):
    allergies: Optional[str] = None
    medications: Optional[str] = None
    conditions: Optional[str] = None
    blood_type: Optional[str] = Field(alias="bloodType", default=None)
    observations: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)


class HealthProfileResponse(BaseModel):
    id: uuid.UUID
    allergies: Optional[str] = None
    medications: Optional[str] = None
    conditions: Optional[str] = None
    blood_type: Optional[str] = None
    observations: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# EmergencyContact schemas
class EmergencyContactCreate(BaseModel):
    name: str
    phone: str
    relationship_type: str = Field(alias="relationshipType")
    model_config = ConfigDict(populate_by_name=True)


class EmergencyContactResponse(BaseModel):
    id: uuid.UUID
    name: str
    phone: str
    relationship_type: str
    model_config = ConfigDict(from_attributes=True)


# BeltPromotion schemas
class BeltPromotionCreate(BaseModel):
    previous_belt: str = Field(alias="previousBelt")
    previous_degree: int = Field(alias="previousDegree")
    new_belt: str = Field(alias="newBelt")
    new_degree: int = Field(alias="newDegree")
    promoted_by: str = Field(alias="promotedBy")
    date: date
    notes: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)


class BeltPromotionResponse(BaseModel):
    id: uuid.UUID
    previous_belt: str
    previous_degree: int
    new_belt: str
    new_degree: int
    promoted_by: str
    date: date
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# InstructorFeedback schemas
class InstructorFeedbackCreate(BaseModel):
    text: str
    date: date


class InstructorFeedbackResponse(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    text: str
    date: date
    model_config = ConfigDict(from_attributes=True)


# StudentContribution schemas
class StudentContributionCreate(BaseModel):
    reference: str
    amount: Decimal
    date: date
    method: str
    receipt_url: Optional[str] = Field(alias="receiptUrl", default=None)
    model_config = ConfigDict(populate_by_name=True)


class StudentContributionResponse(BaseModel):
    id: uuid.UUID
    reference: str
    amount: Decimal
    date: date
    method: str
    receipt_url: Optional[str] = None
    status: str
    model_config = ConfigDict(from_attributes=True)


# StudentDocument schemas
class StudentDocumentCreate(BaseModel):
    type: str
    file_url: str = Field(alias="fileUrl")
    model_config = ConfigDict(populate_by_name=True)


class StudentDocumentResponse(BaseModel):
    id: uuid.UUID
    type: str
    file_url: str
    uploaded_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Full detail response
class StudentDetailResponse(StudentResponse):
    rg: Optional[str] = None
    address: Optional[dict] = None
    guardians: List[GuardianResponse] = []
    school_info: Optional[SchoolInfoResponse] = None
    health_profile: Optional[HealthProfileResponse] = None
    emergency_contacts: List[EmergencyContactResponse] = []
    promotions: List[BeltPromotionResponse] = []
    contributions: List[StudentContributionResponse] = []
    documents: List[StudentDocumentResponse] = []
