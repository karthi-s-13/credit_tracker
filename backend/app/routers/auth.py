from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Student
from ..schemas import LoginRequest, LoginResponse, StudentOut

router = APIRouter(prefix="/auth", tags=["auth"])

# Department code mapping
DEPT_MAP = {
    "23": "AIDS",
    "01": "CSE",
    "02": "ECE",
    "03": "EEE",
    "04": "MECH",
    "05": "CIVIL",
}


def parse_register_number(reg: str):
    """
    Format: CCYYDDDSSS
    CC = college code (2 digits)
    YY = year of joining (2 digits)
    DD = department code (2 digits) — but in the example 212224230116:
         2122 = college(4), 24 = year, 23 = dept, 0116 = student id
    Let's handle: first 4 = college, next 2 = year, next 2 = dept, rest = student id
    """
    reg = reg.strip()
    if len(reg) < 10:
        raise ValueError("Register number too short")
    year_of_joining = int("20" + reg[4:6])
    dept_code = reg[6:8]
    return year_of_joining, dept_code


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    reg = payload.register_number.strip()
    if not reg.isdigit() or len(reg) < 10:
        raise HTTPException(status_code=400, detail="Invalid register number format")

    try:
        year_of_joining, dept_code = parse_register_number(reg)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    dept_name = DEPT_MAP.get(dept_code)

    # Upsert student
    student = db.query(Student).filter(Student.register_number == reg).first()
    if not student:
        student = Student(
            register_number=reg,
            name=payload.name,
            year_of_joining=year_of_joining,
            dept_code=dept_code,
            dept_name=dept_name or f"DEPT_{dept_code}",
            is_lateral_entry=0,
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    elif payload.name and not student.name:
        student.name = payload.name
        db.commit()
        db.refresh(student)

    return LoginResponse(
        student=StudentOut.model_validate(student),
        message="Login successful",
    )


@router.get("/student/{register_number}", response_model=StudentOut)
def get_student(register_number: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.register_number == register_number).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
