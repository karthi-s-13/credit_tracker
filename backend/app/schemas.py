from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


# ─── Course ──────────────────────────────────────────────────────────────────

class CourseBase(BaseModel):
    id: int
    sno: Optional[int] = None
    department: str
    category: Optional[str] = None
    course_code_r2024: Optional[str] = None
    course_code_r2019: Optional[str] = None
    course_title: str
    prerequisite: Optional[str] = None
    theory_credits: int = 0
    practical_credits: int = 0
    total_credits: int = 0
    cgpa_type: Optional[str] = None
    course_type: Optional[str] = None
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class CourseOut(CourseBase):
    pass


# ─── Student ─────────────────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    register_number: str
    name: Optional[str] = None
    is_lateral_entry: Optional[int] = 0


class StudentOut(BaseModel):
    id: int
    register_number: str
    name: Optional[str] = None
    year_of_joining: Optional[int] = None
    dept_code: Optional[str] = None
    dept_name: Optional[str] = None
    is_lateral_entry: int = 0

    class Config:
        from_attributes = True


# ─── Progress ────────────────────────────────────────────────────────────────

class ProgressStatusEnum(str, Enum):
    completed = "completed"
    pending = "pending"


class ProgressSourceEnum(str, Enum):
    ocr = "ocr"
    manual = "manual"


class ProgressToggle(BaseModel):
    register_number: str
    course_id: int
    status: ProgressStatusEnum
    source: ProgressSourceEnum = ProgressSourceEnum.manual
    grade: Optional[str] = None
    grade_point: Optional[str] = None


class ProgressBulkCreate(BaseModel):
    register_number: str
    entries: List[dict]   # [{course_id, status, source, grade, grade_point}]


class ProgressOut(BaseModel):
    id: int
    course_id: int
    status: str
    source: str
    grade: Optional[str] = None
    grade_point: Optional[str] = None
    course: CourseOut

    class Config:
        from_attributes = True


# ─── OCR ─────────────────────────────────────────────────────────────────────

class OcrMatch(BaseModel):
    course_id: int
    course_code: str
    course_title: str
    category: Optional[str]
    total_credits: int
    matched_text: str
    confidence: float
    grade: Optional[str] = None
    grade_point: Optional[str] = None
    result_status: Optional[str] = None


class OcrResult(BaseModel):
    matches: List[OcrMatch]
    unmatched: List[str]


# ─── Auth ────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    register_number: str
    name: Optional[str] = None


class LoginResponse(BaseModel):
    student: StudentOut
    message: str
