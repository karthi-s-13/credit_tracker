from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, UniqueConstraint, Table, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base, engine

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    register_number = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    year_of_joining = Column(Integer, nullable=True)
    dept_code = Column(String(5), nullable=True)
    dept_name = Column(String(50), nullable=True)
    is_lateral_entry = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    progress_entries = relationship("StudentProgress", back_populates="student", cascade="all, delete-orphan")


class ProgressStatusEnum(str, enum.Enum):
    completed = "completed"
    enrolled = "enrolled"
    pending = "pending"


class ProgressSourceEnum(str, enum.Enum):
    ocr = "ocr"
    manual = "manual"


class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_table = Column(String(50), nullable=False)
    course_id = Column(Integer, nullable=False)
    status = Column(Enum(ProgressStatusEnum), default=ProgressStatusEnum.completed, nullable=False)
    source = Column(Enum(ProgressSourceEnum), default=ProgressSourceEnum.manual, nullable=False)
    grade = Column(String(5), nullable=True)
    grade_point = Column(String(5), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    student = relationship("Student", back_populates="progress_entries")

    __table_args__ = (UniqueConstraint("student_id", "course_table", "course_id", name="uq_student_course_dynamic"),)


_dynamic_course_models = {}

def get_dynamic_course_model(table_name: str):
    """
    Returns a SQLAlchemy model class for a dynamically created course table.
    Caches the model to avoid re-creation errors.
    """
    if table_name in _dynamic_course_models:
        return _dynamic_course_models[table_name]

    class DynamicCourse(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}

        id = Column(Integer, primary_key=True, index=True)
        sno = Column(Integer, nullable=True)
        department = Column(String(10), index=True, nullable=False)
        category = Column(String(50), index=True, nullable=True)
        course_code_r2024 = Column(String(20), index=True, nullable=True)
        course_code_r2019 = Column(String(30), nullable=True)
        course_title = Column(String(255), nullable=False)
        prerequisite = Column(String(255), nullable=True)
        theory_credits = Column(Integer, default=0)
        practical_credits = Column(Integer, default=0)
        total_credits = Column(Integer, default=0)
        cgpa_type = Column(String(20), nullable=True)
        course_type = Column(String(100), nullable=True)
        remarks = Column(Text, nullable=True)

    _dynamic_course_models[table_name] = DynamicCourse
    return DynamicCourse
