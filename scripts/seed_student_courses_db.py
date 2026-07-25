import json
import os
import sys
import time

# Ensure backend app is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

# pyrefly: ignore [missing-import]
from app.database import engine, SessionLocal, Base
# pyrefly: ignore [missing-import]
from app.models import Student, StudentProgress, get_dynamic_course_model
# pyrefly: ignore [missing-import]
from app.routers.auth import DEPT_MAP, parse_register_number
from sqlalchemy import inspect, text

def safe_int(val, default=0):
    try:
        return int(str(val).strip())
    except (ValueError, TypeError):
        return default

def seed_database():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    json_paths = [
        os.path.join(base_dir, "data", "students", "student_courses_extracted.json"),
        os.path.join(base_dir, "student_courses_extracted.json")
    ]
    json_path = next((p for p in json_paths if os.path.exists(p)), None)
    if not json_path:
        print("Error: student_courses_extracted.json not found.")
        return

    print(f"Loading student courses from {json_path}...")
    t0 = time.time()
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} records in {time.time() - t0:.2f}s.")

    # 1. Group records by Student Register Number
    student_records = {}
    for row in data:
        reg = (row.get("Register Number") or "").strip()
        if not reg or len(reg) < 10:
            continue
        if reg not in student_records:
            student_records[reg] = {
                "name": (row.get("Name") or "").strip(),
                "dept_in_json": (row.get("Dept") or "").strip(),
                "courses": []
            }
        if not student_records[reg]["name"] and row.get("Name"):
            student_records[reg]["name"] = row.get("Name").strip()
        student_records[reg]["courses"].append(row)

    print(f"Found {len(student_records)} unique students.")

    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)

        # 2. Upsert Students
        print("Upserting Students into Database...")
        existing_students = {s.register_number: s for s in db.query(Student).all()}
        new_students = []

        for reg, sdata in student_records.items():
            try:
                year_of_joining, dept_code = parse_register_number(reg)
            except Exception:
                year_of_joining, dept_code = 2024, reg[6:8] if len(reg) >= 8 else "00"

            dept_name = DEPT_MAP.get(dept_code, sdata["dept_in_json"] or f"DEPT_{dept_code}")

            if reg in existing_students:
                s = existing_students[reg]
                if sdata["name"] and s.name != sdata["name"]:
                    s.name = sdata["name"]
                s.year_of_joining = year_of_joining
                s.dept_code = dept_code
                s.dept_name = dept_name
            else:
                s = Student(
                    register_number=reg,
                    name=sdata["name"] or f"Student {reg[-4:]}",
                    year_of_joining=year_of_joining,
                    dept_code=dept_code,
                    dept_name=dept_name,
                    is_lateral_entry=0
                )
                db.add(s)
                new_students.append(s)

        db.commit()

        student_map = {s.register_number: s for s in db.query(Student).all()}
        print(f"Total students in DB now: {len(student_map)}")

        # 3. Ensure department dynamic course tables exist & populate missing courses
        print("Ensuring dynamic course tables exist...")
        course_id_cache = {}

        dept_year_tables = set()
        for reg, sdata in student_records.items():
            student = student_map[reg]
            dept = (student.dept_name or f"dept{student.dept_code}").lower()
            year = student.year_of_joining or 2024
            table_name = f"{dept}_course_{year}"
            dept_year_tables.add((table_name, student.dept_name or dept.upper(), year))

        for table_name, dept_name_upper, year in dept_year_tables:
            CourseModel = get_dynamic_course_model(table_name)
            Base.metadata.create_all(bind=engine, tables=[CourseModel.__table__])
        
        db.commit()

        for table_name, dept_name_upper, year in dept_year_tables:
            CourseModel = get_dynamic_course_model(table_name)
            existing_courses = db.query(CourseModel).all()
            for c in existing_courses:
                if c.course_code_r2024:
                    course_id_cache[(table_name, "code", c.course_code_r2024.strip().upper())] = c.id
                if c.course_title:
                    course_id_cache[(table_name, "title", c.course_title.strip().lower())] = c.id

        added_courses_count = 0
        for reg, sdata in student_records.items():
            student = student_map[reg]
            dept = (student.dept_name or f"dept{student.dept_code}").lower()
            year = student.year_of_joining or 2024
            table_name = f"{dept}_course_{year}"
            CourseModel = get_dynamic_course_model(table_name)

            for crow in sdata["courses"]:
                code = (crow.get("24 Code") or "").strip()
                title = (crow.get("Course Name") or "").strip()
                category = (crow.get("Category") or "").strip() or "PC"
                credits_val = safe_int(crow.get("credits"), 3)

                code_key = (table_name, "code", code.upper()) if code else None
                title_key = (table_name, "title", title.lower()) if title else None

                if (code_key and code_key in course_id_cache) or (title_key and title_key in course_id_cache):
                    continue

                new_course = CourseModel(
                    sno=999,
                    department=student.dept_name or dept.upper(),
                    category=category,
                    course_code_r2024=code or None,
                    course_code_r2019=(crow.get("19 CODE") or "").strip() or None,
                    course_title=title or "Unknown Course",
                    theory_credits=credits_val,
                    practical_credits=0,
                    total_credits=credits_val,
                    course_type="Regular"
                )
                db.add(new_course)
                db.flush()
                added_courses_count += 1

                if code:
                    course_id_cache[(table_name, "code", code.upper())] = new_course.id
                if title:
                    course_id_cache[(table_name, "title", title.lower())] = new_course.id

        if added_courses_count > 0:
            db.commit()
            print(f"Added {added_courses_count} new courses to dynamic curriculum tables.")

        # 4. Seed / Sync Student Progress records
        print("Seeding Student Progress records...")
        existing_progress = {
            (p.student_id, p.course_table, p.course_id): p
            for p in db.query(StudentProgress).all()
        }

        new_progress_objects = []
        updated_count = 0

        for reg, sdata in student_records.items():
            student = student_map[reg]
            dept = (student.dept_name or f"dept{student.dept_code}").lower()
            year = student.year_of_joining or 2024
            table_name = f"{dept}_course_{year}"

            for crow in sdata["courses"]:
                code = (crow.get("24 Code") or "").strip()
                title = (crow.get("Course Name") or "").strip()
                status_raw = (crow.get("Status") or "").strip()
                
                status_raw_lower = status_raw.lower()
                if status_raw_lower in ["pass", "completed"]:
                    status_val = "completed"
                elif status_raw_lower == "enrolled":
                    status_val = "enrolled"
                else:
                    status_val = "pending"

                code_key = (table_name, "code", code.upper()) if code else None
                title_key = (table_name, "title", title.lower()) if title else None

                course_id = None
                if code_key and code_key in course_id_cache:
                    course_id = course_id_cache[code_key]
                elif title_key and title_key in course_id_cache:
                    course_id = course_id_cache[title_key]

                if not course_id:
                    continue

                prog_key = (student.id, table_name, course_id)
                if prog_key in existing_progress:
                    existing_p = existing_progress[prog_key]
                    if existing_p.status != status_val:
                        existing_p.status = status_val
                        updated_count += 1
                else:
                    p = StudentProgress(
                        student_id=student.id,
                        course_table=table_name,
                        course_id=course_id,
                        status=status_val,
                        source="ocr"
                    )
                    new_progress_objects.append(p)
                    existing_progress[prog_key] = p

        print(f"Prepared {len(new_progress_objects)} new progress entries and {updated_count} updates.")
        
        batch_size = 5000
        for i in range(0, len(new_progress_objects), batch_size):
            db.bulk_save_objects(new_progress_objects[i:i + batch_size])
            
        db.commit()
        print("Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
