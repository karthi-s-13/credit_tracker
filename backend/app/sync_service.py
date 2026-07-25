import json
import os
import threading
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from .models import Student, StudentProgress, get_dynamic_course_model
from .database import engine
import logging

logger = logging.getLogger(__name__)

def _get_json_path():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    candidate_paths = [
        os.path.join(base_dir, "data", "students", "student_courses_extracted.json"),
        os.path.join(base_dir, "student_courses_extracted.json")
    ]
    return next((p for p in candidate_paths if os.path.exists(p)), candidate_paths[0])

_cache_lock = threading.Lock()
_student_courses_cache: Dict[str, List[Dict[str, Any]]] = {}
_cache_loaded = False

def _load_cache():
    global _cache_loaded, _student_courses_cache
    if _cache_loaded:
        return

    json_path = _get_json_path()
    with _cache_lock:
        if _cache_loaded:
            return
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            for record in data:
                reg_no = record.get("Register Number")
                if not reg_no:
                    continue
                if reg_no not in _student_courses_cache:
                    _student_courses_cache[reg_no] = []
                _student_courses_cache[reg_no].append(record)
                
            _cache_loaded = True
            logger.info(f"Loaded {len(_student_courses_cache)} student records from JSON.")
        except Exception as e:
            logger.error(f"Failed to load student courses JSON: {e}")
            # Even if it fails, mark as loaded to avoid spamming file read attempts
            _cache_loaded = True

def get_student_courses_from_json(register_number: str) -> List[Dict[str, Any]]:
    if not _cache_loaded:
        _load_cache()
    return _student_courses_cache.get(register_number, [])

def _get_table_name(student: Student) -> str:
    dept = (student.dept_name or f"dept{student.dept_code}").lower()
    year = student.year_of_joining or "2024"
    return f"{dept}_course_{year}"

def sync_student_courses(student: Student, db: Session):
    courses_data = get_student_courses_from_json(student.register_number)
    if not courses_data:
        return  # No data in JSON for this student

    table_name = _get_table_name(student)
    
    if not engine.dialect.has_table(engine.connect(), table_name):
        return  # Table doesn't exist, can't sync
        
    CourseModel = get_dynamic_course_model(table_name)
    
    # Map code and title to status from JSON
    code_to_status = {}
    title_to_status = {}
    for c in courses_data:
        raw_st = (c.get("Status") or "").strip().lower()
        if raw_st in ["pass", "completed"]:
            st_val = "completed"
        elif raw_st == "enrolled":
            st_val = "enrolled"
        else:
            st_val = "pending"

        code = (c.get("24 Code") or "").strip().upper()
        title = (c.get("Course Name") or "").strip().lower()
        if code:
            code_to_status[code] = st_val
        if title:
            title_to_status[title] = st_val

    # Find the corresponding courses in the dynamic course table
    db_courses = db.query(CourseModel).all()
    
    course_id_to_status = {}
    for c in db_courses:
        c_code = (c.course_code_r2024 or "").strip().upper()
        c_title = (c.course_title or "").strip().lower()
        if c_code and c_code in code_to_status:
            course_id_to_status[c.id] = code_to_status[c_code]
        elif c_title and c_title in title_to_status:
            course_id_to_status[c.id] = title_to_status[c_title]
        
    # Get existing progress
    existing_progress = (
        db.query(StudentProgress)
        .filter(
            StudentProgress.student_id == student.id,
            StudentProgress.course_table == table_name
        )
        .all()
    )
    existing_course_ids = {p.course_id: p for p in existing_progress}

    # Upsert logic
    for course_id, status in course_id_to_status.items():
        if course_id in existing_course_ids:
            p = existing_course_ids[course_id]
            p.status = status
            # Retain existing source if possible, or mark as ocr/manual
        else:
            new_entry = StudentProgress(
                student_id=student.id,
                course_table=table_name,
                course_id=course_id,
                status=status,
                source="ocr"  # Since it's extracted from PDF
            )
            db.add(new_entry)
            
    db.commit()
