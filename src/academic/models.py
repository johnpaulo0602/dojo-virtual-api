import uuid
from datetime import date
from typing import Optional, List

from sqlalchemy import String, Date, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base

class School(Base):
    __tablename__ = "schools"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)

class Student(Base):
    __tablename__ = "students"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    cpf: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    rg: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    matricula: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    belt_name: Mapped[str] = mapped_column(String, nullable=False)
    belt_degree: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="ativo")
    address: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    guardians: Mapped[List["Guardian"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    school_info: Mapped[Optional["StudentSchoolInfo"]] = relationship(back_populates="student", uselist=False, cascade="all, delete-orphan")
    health_profile: Mapped[Optional["StudentHealthProfile"]] = relationship(back_populates="student", uselist=False, cascade="all, delete-orphan")

class Guardian(Base):
    __tablename__ = "guardians"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    cpf: Mapped[str] = mapped_column(String, nullable=False)
    relationship_type: Mapped[str] = mapped_column(String, nullable=False) # mae, pai, outro
    phone: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    profession: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_primary: Mapped[bool] = mapped_column(default=False)

    student: Mapped["Student"] = relationship(back_populates="guardians")

class StudentSchoolInfo(Base):
    __tablename__ = "student_school_info"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False)
    school_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False)
    school_level: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    school_year: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    school_shift: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    student: Mapped["Student"] = relationship(back_populates="school_info")

class StudentHealthProfile(Base):
    __tablename__ = "student_health_profiles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False)
    allergies: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    medications: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    conditions: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    blood_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    emergency_phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    observations: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    student: Mapped["Student"] = relationship(back_populates="health_profile")
