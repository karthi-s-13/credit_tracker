from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..models import Student, StudentProgress, Course
from ..schemas import ProgressToggle, ProgressBulkCreate, ProgressOut

router = APIRouter(prefix="/progress", tags=["progress"])


def _get_student(register_number: str, db: Session) -> Student:
    student = db.query(Student).filter(Student.register_number == register_number).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found. Please login first.")
    return student


@router.get("/{register_number}", response_model=List[ProgressOut])
def get_progress(register_number: str, db: Session = Depends(get_db)):
    student = _get_student(register_number, db)
    entries = (
        db.query(StudentProgress)
        .options(joinedload(StudentProgress.course))
        .filter(StudentProgress.student_id == student.id)
        .all()
    )
    return entries


@router.post("/toggle", response_model=ProgressOut)
def toggle_progress(payload: ProgressToggle, db: Session = Depends(get_db)):
    student = _get_student(payload.register_number, db)

    # Verify course exists
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = (
        db.query(StudentProgress)
        .filter(
            StudentProgress.student_id == student.id,
            StudentProgress.course_id == payload.course_id,
        )
        .first()
    )

    if existing:
        if payload.status.value == "pending":
            # Remove completion
            db.delete(existing)
            db.commit()
            # Return a dummy with pending status
            return ProgressOut(
                id=0,
                course_id=payload.course_id,
                status="pending",
                source=payload.source.value,
                grade=None,
                grade_point=None,
                course=course,
            )
        existing.status = payload.status.value
        existing.source = payload.source.value
        if payload.grade:
            existing.grade = payload.grade
        if payload.grade_point:
            existing.grade_point = payload.grade_point
        db.commit()
        db.refresh(existing)
        return existing
    else:
        if payload.status.value == "pending":
            # Nothing to remove
            return ProgressOut(
                id=0,
                course_id=payload.course_id,
                status="pending",
                source=payload.source.value,
                grade=None,
                grade_point=None,
                course=course,
            )
        new_entry = StudentProgress(
            student_id=student.id,
            course_id=payload.course_id,
            status=payload.status.value,
            source=payload.source.value,
            grade=payload.grade,
            grade_point=payload.grade_point,
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        return new_entry


@router.post("/bulk", response_model=List[ProgressOut])
def bulk_create_progress(payload: ProgressBulkCreate, db: Session = Depends(get_db)):
    """Save multiple course completions at once (e.g. from OCR results)."""
    student = _get_student(payload.register_number, db)
    results = []

    for entry in payload.entries:
        course_id = entry.get("course_id")
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            continue

        existing = (
            db.query(StudentProgress)
            .filter(
                StudentProgress.student_id == student.id,
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
            results.append(existing)
        else:
            new_entry = StudentProgress(
                student_id=student.id,
                course_id=course_id,
                status=entry.get("status", "completed"),
                source=entry.get("source", "ocr"),
                grade=entry.get("grade"),
                grade_point=entry.get("grade_point"),
            )
            db.add(new_entry)
            db.commit()
            db.refresh(new_entry)
            results.append(new_entry)

    return results


@router.delete("/{register_number}/{course_id}")
def delete_progress(register_number: str, course_id: int, db: Session = Depends(get_db)):
    student = _get_student(register_number, db)
    entry = (
        db.query(StudentProgress)
        .filter(
            StudentProgress.student_id == student.id,
            StudentProgress.course_id == course_id,
        )
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Progress entry not found")
    db.delete(entry)
    db.commit()
    return {"detail": "Deleted successfully"}
