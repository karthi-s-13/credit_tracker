from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db, engine
from ..models import Student, StudentProgress, get_dynamic_course_model
from ..schemas import ProgressToggle, ProgressBulkCreate, ProgressOut, CourseOut

router = APIRouter(prefix="/progress", tags=["progress"])


def _get_student(register_number: str, db: Session) -> Student:
    student = db.query(Student).filter(Student.register_number == register_number).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found. Please login first.")
    return student

def _get_table_name(student: Student) -> str:
    dept = (student.dept_name or f"dept{student.dept_code}").lower()
    year = student.year_of_joining or "2024" # fallback
    return f"{dept}_course_{year}"


@router.get("/{register_number}", response_model=List[ProgressOut])
def get_progress(register_number: str, db: Session = Depends(get_db)):
    student = _get_student(register_number, db)
    entries = (
        db.query(StudentProgress)
        .filter(StudentProgress.student_id == student.id)
        .all()
    )
    
    # We must attach `.course` manually
    results = []
    
    # Batch query courses per table
    table_to_course_ids = {}
    for entry in entries:
        if entry.course_table not in table_to_course_ids:
            table_to_course_ids[entry.course_table] = []
        table_to_course_ids[entry.course_table].append(entry.course_id)
        
    course_cache = {}
    for table_name, course_ids in table_to_course_ids.items():
        CourseModel = get_dynamic_course_model(table_name)
        if engine.dialect.has_table(engine.connect(), table_name):
            courses = db.query(CourseModel).filter(CourseModel.id.in_(course_ids)).all()
            for c in courses:
                course_cache[(table_name, c.id)] = CourseOut.model_validate(c)
                
    for entry in entries:
        # Manually attach course object before validation
        entry.course = course_cache.get((entry.course_table, entry.course_id))
        out = ProgressOut.model_validate(entry)
        results.append(out)
        
    return results


@router.post("/toggle", response_model=ProgressOut)
def toggle_progress(payload: ProgressToggle, db: Session = Depends(get_db)):
    student = _get_student(payload.register_number, db)
    table_name = _get_table_name(student)
    CourseModel = get_dynamic_course_model(table_name)
    
    if not engine.dialect.has_table(engine.connect(), table_name):
        raise HTTPException(status_code=404, detail=f"Course table {table_name} not found.")

    # Verify course exists
    course = db.query(CourseModel).filter(CourseModel.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = (
        db.query(StudentProgress)
        .filter(
            StudentProgress.student_id == student.id,
            StudentProgress.course_table == table_name,
            StudentProgress.course_id == payload.course_id,
        )
        .first()
    )

    if existing:
        if payload.status.value == "pending":
            db.delete(existing)
            db.commit()
            return ProgressOut(
                id=0,
                course_table=table_name,
                course_id=payload.course_id,
                status="pending",
                source=payload.source.value,
                grade=None,
                grade_point=None,
                course=CourseOut.model_validate(course),
            )
        existing.status = payload.status.value
        existing.source = payload.source.value
        if payload.grade:
            existing.grade = payload.grade
        if payload.grade_point:
            existing.grade_point = payload.grade_point
        db.commit()
        db.refresh(existing)
        
        out = ProgressOut.model_validate(existing)
        out.course = CourseOut.model_validate(course)
        return out
    else:
        if payload.status.value == "pending":
            return ProgressOut(
                id=0,
                course_table=table_name,
                course_id=payload.course_id,
                status="pending",
                source=payload.source.value,
                grade=None,
                grade_point=None,
                course=CourseOut.model_validate(course),
            )
        new_entry = StudentProgress(
            student_id=student.id,
            course_table=table_name,
            course_id=payload.course_id,
            status=payload.status.value,
            source=payload.source.value,
            grade=payload.grade,
            grade_point=payload.grade_point,
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        
        out = ProgressOut.model_validate(new_entry)
        out.course = CourseOut.model_validate(course)
        return out


@router.post("/bulk", response_model=List[ProgressOut])
def bulk_create_progress(payload: ProgressBulkCreate, db: Session = Depends(get_db)):
    student = _get_student(payload.register_number, db)
    table_name = _get_table_name(student)
    CourseModel = get_dynamic_course_model(table_name)
    results = []

    if not engine.dialect.has_table(engine.connect(), table_name):
        return []

    for entry in payload.entries:
        course_id = entry.get("course_id")
        course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
        if not course:
            continue

        existing = (
            db.query(StudentProgress)
            .filter(
                StudentProgress.student_id == student.id,
                StudentProgress.course_table == table_name,
                StudentProgress.course_id == course_id,
            )
            .first()
        )

        if existing:
            existing.status = entry.get("status", "completed")
            existing.source = entry.get("source", "ocr")
            existing.grade = entry.get("grade")
            existing.grade_point = entry.get("grade_point")
            db.commit()
            db.refresh(existing)
            out = ProgressOut.model_validate(existing)
        else:
            new_entry = StudentProgress(
                student_id=student.id,
                course_table=table_name,
                course_id=course_id,
                status=entry.get("status", "completed"),
                source=entry.get("source", "ocr"),
                grade=entry.get("grade"),
                grade_point=entry.get("grade_point"),
            )
            db.add(new_entry)
            db.commit()
            db.refresh(new_entry)
            out = ProgressOut.model_validate(new_entry)

        out.course = CourseOut.model_validate(course)
        results.append(out)

    return results


@router.delete("/{register_number}/{course_id}")
def delete_progress(register_number: str, course_id: int, db: Session = Depends(get_db)):
    student = _get_student(register_number, db)
    table_name = _get_table_name(student)
    
    entry = (
        db.query(StudentProgress)
        .filter(
            StudentProgress.student_id == student.id,
            StudentProgress.course_table == table_name,
            StudentProgress.course_id == course_id,
        )
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Progress entry not found")
    db.delete(entry)
    db.commit()
    return {"detail": "Deleted successfully"}
