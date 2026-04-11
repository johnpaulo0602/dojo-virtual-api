import uuid
from datetime import time, date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

class ClassScheduleSchema(BaseModel):
    day_of_week: int = Field(alias="dayOfWeek")
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")

    model_config = ConfigDict(populate_by_name=True)

class ClassGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    instructor_id: uuid.UUID = Field(alias="instructorId")
    instructor_name: str = Field(alias="instructorName")
    location: str
    capacity: int
    status: str = "ativa"
    age_range: Optional[str] = Field(alias="ageRange", default=None)
    belt_range: Optional[str] = Field(alias="beltRange", default=None)
    schedules: List[ClassScheduleSchema] = []

    model_config = ConfigDict(populate_by_name=True)

class ClassGroupResponse(ClassGroupCreate):
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class LessonGenerateRequest(BaseModel):
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")

    model_config = ConfigDict(populate_by_name=True)

class LessonResponse(BaseModel):
    id: uuid.UUID
    class_group_id: uuid.UUID = Field(alias="classGroupId")
    date: date
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")
    location: str
    instructor_name: str = Field(alias="instructorName")
    status: str
    topic: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class AttendanceUpdate(BaseModel):
    student_id: uuid.UUID | None = Field(alias="studentId", default=None)
    present: bool

    model_config = ConfigDict(populate_by_name=True)

class AttendanceBatchUpdate(BaseModel):
    records: List[AttendanceUpdate]


class ClassGroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    instructor_id: uuid.UUID | None = None
    instructor_name: str | None = None
    location: str | None = None
    capacity: int | None = None
    status: str | None = None
    age_range: str | None = None
    belt_range: str | None = None


class ClassGroupDetailResponse(ClassGroupResponse):
    lessons_count: int = 0
    enrolled_count: int = 0


class AttendanceRecordResponse(BaseModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    present: bool
    checked_in_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class LessonDetailResponse(LessonResponse):
    class_group: ClassGroupResponse
    attendance: list[AttendanceRecordResponse] = []