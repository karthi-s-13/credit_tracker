from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import get_dynamic_course_model
from ..schemas import CourseOut

router = APIRouter(prefix="/curriculum", tags=["curriculum"])

DEPT_NAME_MAP = {
    "02": "BME",
    "03": "CIVIL",
    "04": "CSE",
    "05": "EEE",
    "06": "ECE",
    "08": "MECH",
    "10": "CSECS",
    "11": "CSEIOT",
    "21": "CHEM",
    "22": "IT",
    "23": "AIDS",
    "24": "AIML",
    "25": "AGRI",
    # Fallbacks
    "AIDS": "AIDS",
    "CSECS": "CSECS"
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

CATEGORY_CREDITS = {
    "AIDS": {
        "regular": {"HS": 14, "BS": 23, "ES": 28, "PC": 56, "PE": 16, "OE": 12, "EEC": 16, "MC": 4},
        "le": {"HS": 3, "BS": 16, "ES": 15, "PC": 48, "PE": 15, "OE": 12, "EEC": 16, "MC": 4}
    },
    "CSECS": {
        "regular": {"HS": 14, "BS": 25, "ES": 28, "PC": 56, "PE": 16, "OE": 12, "EEC": 16, "MC": 4},
        "le": {"HS": 3, "BS": 16, "ES": 15, "PC": 48, "PE": 15, "OE": 12, "EEC": 16, "MC": 4}
    },
    "AGRI": {
        "regular": {"HS": 12, "BS": 23, "ES": 45, "PC": 54, "PE": 9, "OE": 6, "EEC": 33, "MC": 2},
        "le": {"HS": 2, "BS": 4, "ES": 27, "PC": 54, "PE": 9, "OE": 6, "EEC": 33, "MC": 2}
    },
    "AIML": {
        "regular": {"HS": 14, "BS": 27, "ES": 28, "PC": 51, "PE": 16, "OE": 12, "EEC": 16, "MC": 4},
        "le": {"HS": 3, "BS": 20, "ES": 12, "PC": 43, "PE": 16, "OE": 12, "EEC": 16, "MC": 4}
    },
    "BME": {
        "regular": {"HS": 10, "BS": 23, "ES": 30, "PC": 60, "PE": 18, "OE": 7, "EEC": 18, "MC": 2},
        "le": {"HS": 0, "BS": 12, "ES": 18, "PC": 57, "PE": 18, "OE": 7, "EEC": 18, "MC": 2}
    },
    "CIVIL": {
        "regular": {"HS": 10, "BS": 22, "ES": 25, "PC": 62, "PE": 15, "OE": 12, "EEC": 16, "MC": 3},
        "le": {"HS": 2, "BS": 6, "ES": 16, "PC": 62, "PE": 15, "OE": 12, "EEC": 16, "MC": 3}
    },
    "CSE": {
        "regular": {"HS": 13, "BS": 25, "ES": 25, "PC": 56, "PE": 16, "OE": 12, "EEC": 16, "MC": 4},
        "le": {"HS": 3, "BS": 10, "ES": 12, "PC": 56, "PE": 16, "OE": 12, "EEC": 16, "MC": 4}
    },
    "CSEIOT": {
        "regular": {"HS": 14, "BS": 25, "ES": 28, "PC": 56, "PE": 16, "OE": 12, "EEC": 16, "MC": 4},
        "le": {"HS": 3, "BS": 18, "ES": 12, "PC": 47, "PE": 16, "OE": 12, "EEC": 16, "MC": 4}
    },
    "ECE": {
        "regular": {"HS": 13, "BS": 21, "ES": 23, "PC": 61, "PE": 15, "OE": 12, "EEC": 16, "MC": 3},
        "le": {"HS": 4, "BS": 4, "ES": 16, "PC": 61, "PE": 15, "OE": 12, "EEC": 16, "MC": 3}
    },
    "EEE": {
        "regular": {"HS": 11, "BS": 25, "ES": 26, "PC": 57, "PE": 15, "OE": 12, "EEC": 16, "MC": 3},
        "le": {"HS": 3, "BS": 6, "ES": 12, "PC": 57, "PE": 15, "OE": 12, "EEC": 16, "MC": 3}
    },
    "IT": {
        "regular": {"HS": 13, "BS": 25, "ES": 25, "PC": 56, "PE": 16, "OE": 12, "EEC": 16, "MC": 4},
        "le": {"HS": 3, "BS": 10, "ES": 10, "PC": 56, "PE": 16, "OE": 12, "EEC": 16, "MC": 4}
    },
    "MECH": {
        "regular": {"HS": 10, "BS": 25, "ES": 29, "PC": 55, "PE": 18, "OE": 12, "EEC": 16, "MC": 3},
        "le": {"HS": 4, "BS": 6, "ES": 17, "PC": 55, "PE": 18, "OE": 12, "EEC": 16, "MC": 3}
    }
}


@router.get("/{dept_name}/meta")
def get_curriculum_meta(dept_name: str, is_lateral_entry: int = 0):
    dept = dept_name.upper()
    credits_map = CATEGORY_CREDITS.get(dept, CATEGORY_CREDITS["AIDS"])
    credits = credits_map["le"] if is_lateral_entry else credits_map["regular"]
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


@router.get("/{dept_name}/{year}", response_model=List[CourseOut])
def get_curriculum(dept_name: str, year: str, db: Session = Depends(get_db)):
    dept = dept_name.upper()
    table_name = f"{dept.lower()}_course_{year}"
    CourseModel = get_dynamic_course_model(table_name)
    
    from ..database import engine
    if not engine.dialect.has_table(engine.connect(), table_name):
        raise HTTPException(status_code=404, detail=f"No curriculum found for department: {dept} and year: {year}")
        
    courses = db.query(CourseModel).order_by(CourseModel.sno, CourseModel.id).all()
    return courses
