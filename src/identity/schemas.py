import uuid
from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str = ""
    role: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    role: str
    phone: str | None = None
    belt_name: str | None = None
    belt_degree: int | None = None
    specialties: str | None = None
    status: str = "ativo"

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserCreateAdmin(BaseModel):
    email: EmailStr
    name: str
    password: str = ""
    role: str
    phone: str | None = None
    belt_name: str | None = None
    belt_degree: int | None = None
    specialties: str | None = None

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    role: str | None = None
    phone: str | None = None
    belt_name: str | None = None
    belt_degree: int | None = None
    specialties: str | None = None
    status: str | None = None

class ProfileUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class AdminSetPassword(BaseModel):
    new_password: str

class FirstAccessRequest(BaseModel):
    email: EmailStr
    cpf: str
    new_password: str
    confirm_password: str
