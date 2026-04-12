import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, Date, Integer, Boolean, ForeignKey, JSON, Numeric, DateTime, func
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
    profession: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    contributes: Mapped[bool] = mapped_column(Boolean, default=False)
    contribution_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    guardians: Mapped[List["Guardian"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    school_info: Mapped[Optional["StudentSchoolInfo"]] = relationship(back_populates="student", uselist=False, cascade="all, delete-orphan")
    health_profile: Mapped[Optional["StudentHealthProfile"]] = relationship(back_populates="student", uselist=False, cascade="all, delete-orphan")
    emergency_contacts: Mapped[List["EmergencyContact"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    promotions: Mapped[List["BeltPromotion"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    feedbacks: Mapped[List["InstructorFeedback"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    contributions: Mapped[List["StudentContribution"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    documents: Mapped[List["StudentDocument"]] = relationship(back_populates="student", cascade="all, delete-orphan")


class Guardian(Base):
    __tablename__ = "guardians"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    cpf: Mapped[str] = mapped_column(String, nullable=False)
    relationship_type: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    profession: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    student: Mapped["Student"] = relationship(back_populates="guardians")


class StudentSchoolInfo(Base):
    __tablename__ = "student_school_info"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False)
    school_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False)
    is_student: Mapped[bool] = mapped_column(Boolean, default=True)
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
    observations: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    student: Mapped["Student"] = relationship(back_populates="health_profile")


class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    relationship_type: Mapped[str] = mapped_column(String, nullable=False)
    student: Mapped["Student"] = relationship(back_populates="emergency_contacts")


class BeltPromotion(Base):
    __tablename__ = "belt_promotions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    previous_belt: Mapped[str] = mapped_column(String, nullable=False)
    previous_degree: Mapped[int] = mapped_column(Integer, nullable=False)
    new_belt: Mapped[str] = mapped_column(String, nullable=False)
    new_degree: Mapped[int] = mapped_column(Integer, nullable=False)
    promoted_by: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    student: Mapped["Student"] = relationship(back_populates="promotions")


class InstructorFeedback(Base):
    __tablename__ = "instructor_feedbacks"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    student: Mapped["Student"] = relationship(back_populates="feedbacks")


class StudentContribution(Base):
    __tablename__ = "student_contributions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    reference: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    method: Mapped[str] = mapped_column(String, nullable=False)
    receipt_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pago")
    student: Mapped["Student"] = relationship(back_populates="contributions")


class StudentDocument(Base):
    __tablename__ = "student_documents"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    file_url: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    student: Mapped["Student"] = relationship(back_populates="documents")
