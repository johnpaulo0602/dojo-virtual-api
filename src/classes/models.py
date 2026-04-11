# api/src/classes/models.py
import uuid
from datetime import time, date, datetime
from typing import Optional, List

from sqlalchemy import String, Integer, ForeignKey, Date, Time, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base
import src.academic.models  # Ensure students table is known for FK

class ClassGroup(Base):
    __tablename__ = "class_groups"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    instructor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False) # will point to users/staff later
    instructor_name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, default="ativa")
    age_range: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    belt_range: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    schedules: Mapped[List["ClassSchedule"]] = relationship(back_populates="class_group", cascade="all, delete-orphan")
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="class_group", cascade="all, delete-orphan")

class ClassSchedule(Base):
    __tablename__ = "class_schedules"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("class_groups.id", ondelete="CASCADE"), nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False) # 0=Mon, 6=Sun
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    class_group: Mapped["ClassGroup"] = relationship(back_populates="schedules")

class Lesson(Base):
    __tablename__ = "lessons"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("class_groups.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    instructor_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="agendada") # agendada, realizada, cancelada
    topic: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    class_group: Mapped["ClassGroup"] = relationship(back_populates="lessons")
    attendances: Mapped[List["AttendanceRecord"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('class_group_id', 'date', 'start_time', name='uq_lesson_schedule'),
    )

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    present: Mapped[bool] = mapped_column(Boolean, default=False)
    checked_in_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    lesson: Mapped["Lesson"] = relationship(back_populates="attendances")
    
    __table_args__ = (
        UniqueConstraint('lesson_id', 'student_id', name='uq_lesson_student_attendance'),
    )
