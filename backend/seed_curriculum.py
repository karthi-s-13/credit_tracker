"""
Seed script: Load R2024_Curriculum_AIDS.json into the MySQL `courses` table.
Run once: python seed_curriculum.py
"""
import json
import sys
import os

# Add parent so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, Base
from app.models import Course

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "R2024_Curriculum_AIDS.json")

DEPT = "AIDS"


def safe_int(val, default=0):
    try:
        return int(str(val).strip())
    except (ValueError, TypeError):
        return default


def main():
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)

    print(f"Loading curriculum from {JSON_PATH}...")
    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()
    try:
        existing = db.query(Course).filter(Course.department == DEPT).count()
        if existing > 0:
            print(f"  {existing} AIDS courses already in DB. Skipping seed (delete rows to re-seed).")
            return

        inserted = 0
        for item in data:
            course = Course(
                sno=safe_int(item.get("S.No")),
                department=DEPT,
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
        print(f"  ✓ Inserted {inserted} courses for {DEPT} department.")
    except Exception as e:
        db.rollback()
        print(f"  ✗ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
