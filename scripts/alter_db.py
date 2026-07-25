import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database import engine
from sqlalchemy import text

def alter():
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE student_progress MODIFY COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending'"))
        conn.commit()
    print("Database column updated successfully!")

if __name__ == "__main__":
    alter()
