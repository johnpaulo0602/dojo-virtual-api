import uuid
from datetime import date
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

class GuardianCreate(BaseModel):
    name: str
    cpf: str
    relationship_type: str = Field(alias="relationship")
    phone: str
    email: Optional[str] = None
    profession: Optional[str] = None
    is_primary: bool = Field(alias="isPrimary", default=False)

    model_config = ConfigDict(populate_by_name=True)

class SchoolInfoCreate(BaseModel):
    school_id: uuid.UUID = Field(alias="schoolId")
    school_level: Optional[str] = Field(alias="schoolLevel", default=None)
    school_year: Optional[str] = Field(alias="schoolYear", default=None)
    school_shift: Optional[str] = Field(alias="schoolShift", default=None)

    model_config = ConfigDict(populate_by_name=True)

class HealthProfileCreate(BaseModel):
    allergies: Optional[str] = None
    medications: Optional[str] = None
    conditions: Optional[str] = None
    blood_type: Optional[str] = Field(alias="bloodType", default=None)
    emergency_contact: Optional[str] = Field(alias="emergencyContact", default=None)
    emergency_phone: Optional[str] = Field(alias="emergencyPhone", default=None)
    observations: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

class StudentOnboarding(BaseModel):
    name: str
    cpf: str
    rg: Optional[str] = None
    matricula: str
    birth_date: date = Field(alias="birthDate")
    gender: str
    email: Optional[str] = None
    phone: Optional[str] = None
    belt_name: str = Field(alias="beltName")
    belt_degree: int = Field(alias="beltDegree", default=0)
    status: str = "ativo"
    address: Optional[AddressSchema] = None
    
    guardians: List[GuardianCreate] = []
    school_info: Optional[SchoolInfoCreate] = Field(alias="schoolInfo", default=None)
    health: Optional[HealthProfileCreate] = None

    model_config = ConfigDict(populate_by_name=True)

class StudentResponse(BaseModel):
    id: uuid.UUID
    name: str
    cpf: str
    matricula: str
    
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
    name: str | None = None
    address: str | None = None

class GuardianResponse(BaseModel):
    id: uuid.UUID
    name: str
    cpf: str
    relationship_type: str
    phone: str
    email: str | None = None
    profession: str | None = None
    is_primary: bool
    model_config = ConfigDict(from_attributes=True)

class SchoolInfoResponse(BaseModel):
    id: uuid.UUID
    school_id: uuid.UUID
    school_level: str | None = None
    school_year: str | None = None
    school_shift: str | None = None
    model_config = ConfigDict(from_attributes=True)

class HealthProfileResponse(BaseModel):
    id: uuid.UUID
    allergies: str | None = None
    medications: str | None = None
    conditions: str | None = None
    blood_type: str | None = None
    emergency_contact: str | None = None
    emergency_phone: str | None = None
    observations: str | None = None
    model_config = ConfigDict(from_attributes=True)

class StudentDetailResponse(BaseModel):
    id: uuid.UUID
    name: str
    cpf: str
    rg: str | None = None
    matricula: str
    birth_date: date
    gender: str
    email: str | None = None
    phone: str | None = None
    belt_name: str
    belt_degree: int
    status: str
    guardians: list[GuardianResponse]
    school_info: SchoolInfoResponse | None = None
    health_profile: HealthProfileResponse | None = None
    model_config = ConfigDict(from_attributes=True)
