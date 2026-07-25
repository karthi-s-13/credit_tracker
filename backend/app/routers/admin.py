from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, inspect
from typing import List
import json

from ..database import get_db, engine
from ..models import Student, StudentProgress, get_dynamic_course_model, Base
from ..schemas import StudentAdminOut

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/students", response_model=List[StudentAdminOut])
def get_all_students(db: Session = Depends(get_db)):
    """
    Get all students along with their total completed credits from dynamic tables.
    """
    students = db.query(Student).all()
    
    # Get all completed progress entries
    progress_entries = db.query(StudentProgress).filter(StudentProgress.status == "completed").all()
    
    # Group by course_table to batch queries
    table_to_course_ids = {}
    for p in progress_entries:
        if p.course_table not in table_to_course_ids:
            table_to_course_ids[p.course_table] = set()
        table_to_course_ids[p.course_table].add(p.course_id)
        
    # Fetch course details dynamically per table
    inspector = inspect(engine)
    course_credits = {}  # (table, course_id) -> total_credits
    for table_name, course_ids in table_to_course_ids.items():
        CourseModel = get_dynamic_course_model(table_name)
        # Ensure table exists before querying
        if inspector.has_table(table_name):
            courses = db.query(CourseModel.id, CourseModel.total_credits).filter(CourseModel.id.in_(course_ids)).all()
            for cid, credits in courses:
                course_credits[(table_name, cid)] = credits or 0
                
    # Sum credits per student
    student_credits = {}
    for p in progress_entries:
        credits = course_credits.get((p.course_table, p.course_id), 0)
        student_credits[p.student_id] = student_credits.get(p.student_id, 0) + credits
        
    admin_students = []
    for student in students:
        student_data = student.__dict__.copy()
        student_data["total_completed_credits"] = student_credits.get(student.id, 0)
        admin_students.append(student_data)

    return admin_students


def safe_int(val, default=0):
    try:
        return int(str(val).strip())
    except (ValueError, TypeError):
        return default


@router.post("/curriculum/upload")
async def upload_curriculum(
    department: str = Form(...),
    curriculum_year: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a JSON or PDF curriculum file to dynamically create/alter a course table.
    """
    if not (file.filename.endswith(".json") or file.filename.endswith(".pdf")):
        raise HTTPException(status_code=400, detail="Only JSON and PDF files are supported.")
        
    try:
        content = await file.read()
        if file.filename.endswith(".json"):
            data = json.loads(content)
        else:
            # Handle PDF extraction using pdfplumber
            import pdfplumber
            import io
            
            data = []
            headers = [
                "S.No", "Remarks", "Category", "Course Code R2024", 
                "Course Code R2019", "Course Title", "Prerequisite", 
                "Theory Credits", "Practical Credits", "Total Credits", 
                "CGPA/Non-CGPA", "Course Type"
            ]
            
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            if not row or row[0] == "S.No" or row[0] is None:
                                continue
                            
                            row_data = {}
                            for i, header in enumerate(headers):
                                if i < len(row) and row[i] is not None:
                                    cleaned_value = str(row[i]).replace('\n', ' ').strip()
                                else:
                                    cleaned_value = ""
                                row_data[header] = cleaned_value
                            
                            if row_data.get("S.No", "").isdigit():
                                data.append(row_data)
                                
            if not data:
                raise ValueError("Could not extract any courses from the PDF. Ensure the PDF contains tabular data in the expected format.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid file format or extraction error: {str(e)}")
        
    table_name = f"{department.lower()}_course_{curriculum_year}"
    CourseModel = get_dynamic_course_model(table_name)
    
    # Create table if it doesn't exist
    Base.metadata.create_all(bind=engine, tables=[CourseModel.__table__])
    
    # Optionally clear existing data for this curriculum to overwrite
    db.query(CourseModel).delete()
    db.commit()
    
    inserted = 0
    for item in data:
        course = CourseModel(
            sno=safe_int(item.get("S.No")),
            department=department.upper(),
            category=(item.get("Category") or "").strip() or None,
            course_code_r2024=(item.get("Course Code R2024") or "").strip() or None,
            course_code_r2019=(item.get("Course Code R2019") or "").strip() or None,
            course_title=(item.get("Course Title") or "").strip(),
            prerequisite=(item.get("Prerequisite") or "").strip() or None,
            theory_credits=safe_int(item.get("Theory Credits")),
            practical_credits=safe_int(item.get("Practical Credits")),
            total_credits=safe_int(item.get("Total Credits")),
            cgpa_type=(item.get("CGPA/Non-CGPA") or "").strip() or None,
            course_type=(item.get("Course Type") or "").strip() or None,
            remarks=(item.get("Remarks") or "").strip() or None,
        )
        db.add(course)
        inserted += 1
        
    db.commit()
    return {"message": f"Successfully created {table_name} and inserted {inserted} courses."}
