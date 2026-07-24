from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Course
from ..schemas import CourseOut

router = APIRouter(prefix="/curriculum", tags=["curriculum"])

DEPT_NAME_MAP = {
    "AIDS": "AIDS",
    "23": "AIDS",
}

CATEGORY_LABELS = {
    "HS": "Humanities and Science",
    "BS": "Basic Science",
    "ES": "Engineering Science",
    "PC": "Professional Core",
    "PE": "Professional Electives",
    "OE": "Open Electives",
    "EEC": "Employability Enhancement Courses",
    "MC": "Mandatory Courses",
}

CATEGORY_CREDITS_REGULAR = {
    "HS": 14, "BS": 23, "ES": 28, "PC": 56,
    "PE": 16, "OE": 12, "EEC": 16, "MC": 4,
}

CATEGORY_CREDITS_LE = {
    "HS": 3, "BS": 16, "ES": 15, "PC": 48,
    "PE": 15, "OE": 12, "EEC": 16, "MC": 4,
}


@router.get("/{dept_name}", response_model=List[CourseOut])
def get_curriculum(dept_name: str, db: Session = Depends(get_db)):
    dept = dept_name.upper()
    courses = db.query(Course).filter(Course.department == dept).order_by(Course.sno).all()
    if not courses:
        raise HTTPException(status_code=404, detail=f"No curriculum found for department: {dept}")
    return courses


@router.get("/{dept_name}/meta")
def get_curriculum_meta(dept_name: str, is_lateral_entry: int = 0):
    credits = CATEGORY_CREDITS_LE if is_lateral_entry else CATEGORY_CREDITS_REGULAR
    categories = [
        {
            "code": code,
            "label": CATEGORY_LABELS.get(code, code),
            "required_credits": credits.get(code, 0),
        }
        for code in CATEGORY_LABELS.keys()
    ]
    return {
        "department": dept_name.upper(),
        "is_lateral_entry": bool(is_lateral_entry),
        "total_required": sum(credits.values()),
        "categories": categories,
    }
