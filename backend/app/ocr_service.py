"""
OCR Service — PDF → images → PaddleOCR → fuzzy match against curriculum DB
"""
import io
import re
from typing import List, Tuple, Optional

import fitz  # pymupdf
import numpy as np
from PIL import Image
# pyrefly: ignore [missing-import]
from paddleocr import PaddleOCR
# pyrefly: ignore [missing-import]
from rapidfuzz import fuzz, process
from sqlalchemy.orm import Session

from .models import get_dynamic_course_model
from .database import engine

# Singleton OCR instance (heavy to initialise)
_ocr_instance: Optional[PaddleOCR] = None


def get_ocr() -> PaddleOCR:
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    return _ocr_instance


def pdf_to_images(pdf_bytes: bytes) -> List[np.ndarray]:
    """Convert every PDF page to an RGB numpy array."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in doc:
        mat = fitz.Matrix(2.0, 2.0)   # 2× zoom for better OCR
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(np.array(img))
    doc.close()
    return images


def run_ocr_on_images(images: List[np.ndarray]) -> List[str]:
    """Run PaddleOCR and collect all detected text lines."""
    ocr = get_ocr()
    texts = []
    for img in images:
        result = ocr.ocr(img, cls=True)
        if result and result[0]:
            for box in result[0]:
                _, (text, conf) = box
                if conf > 0.5:
                    texts.append(text.strip())
    return texts


def parse_result_lines(texts: List[str]) -> List[dict]:
    """
    Try to reconstruct table rows from raw OCR lines.
    Returns list of {raw_text, grade, grade_point, result_status}
    """
    # Collect lines that look like course identifiers (code or title fragments)
    course_pattern = re.compile(r"^[A-Z]{2,4}\d{4}", re.IGNORECASE)
    grade_pattern = re.compile(r"^(A\+\+|A\+|A|B\+|B|C\+|C|D|F|S|U|W|P)$")
    gp_pattern = re.compile(r"^(10|[1-9])$")
    result_pattern = re.compile(r"(Pass|Fail|Absent|Withheld)", re.IGNORECASE)

    rows = []
    i = 0
    while i < len(texts):
        text = texts[i]
        if course_pattern.match(text):
            row = {
                "raw_text": text,
                "grade": None,
                "grade_point": None,
                "result_status": None,
            }
            # Look ahead for grade, grade_point, result in next 6 lines
            for j in range(i + 1, min(i + 7, len(texts))):
                t = texts[j]
                if not row["grade_point"] and gp_pattern.match(t):
                    row["grade_point"] = t
                if not row["grade"] and grade_pattern.match(t):
                    row["grade"] = t
                if not row["result_status"]:
                    m = result_pattern.search(t)
                    if m:
                        row["result_status"] = m.group()
            rows.append(row)
        i += 1
    return rows


def fuzzy_match_course(text: str, choices: List[Tuple[int, str, str]]) -> Optional[Tuple[int, float]]:
    """
    Match `text` against course codes and titles.
    `choices` is list of (course_id, course_code, course_title).
    Returns (course_id, score) or None if score < 65.
    """
    # Build a flat lookup: course_id → best_score
    best_id = None
    best_score = 0.0

    for course_id, code, title in choices:
        # First try exact code prefix match (highest priority)
        code_clean = (code or "").strip().upper()
        text_upper = text.strip().upper()
        if code_clean and (text_upper.startswith(code_clean) or code_clean in text_upper):
            return (course_id, 100.0)
        # Then try fuzzy title match
        score = fuzz.partial_ratio(text_upper, title.upper())
        if score > best_score:
            best_score = score
            best_id = course_id

    if best_score >= 65:
        return (best_id, best_score)
    return None


def process_pdf(pdf_bytes: bytes, db: Session, table_name: str):
    """
    Full pipeline: PDF → images → OCR → parse → match.
    Returns dict with `matches` and `unmatched` lists.
    """
    from .schemas import OcrMatch, OcrResult

    if not engine.dialect.has_table(engine.connect(), table_name):
        return OcrResult(matches=[], unmatched=["Curriculum table not found for this student."])

    CourseModel = get_dynamic_course_model(table_name)

    # Load all courses for the dynamic table
    courses = db.query(CourseModel).all()
    choices = [(c.id, c.course_code_r2024 or "", c.course_title) for c in courses]
    course_map = {c.id: c for c in courses}

    images = pdf_to_images(pdf_bytes)
    all_texts = run_ocr_on_images(images)
    rows = parse_result_lines(all_texts)

    matches = []
    unmatched = []

    for row in rows:
        result = fuzzy_match_course(row["raw_text"], choices)
        if result:
            course_id, score = result
            c = course_map[course_id]
            matches.append(
                OcrMatch(
                    course_id=c.id,
                    course_code=c.course_code_r2024 or "",
                    course_title=c.course_title,
                    category=c.category,
                    total_credits=c.total_credits,
                    matched_text=row["raw_text"],
                    confidence=round(score, 1),
                    grade=row["grade"],
                    grade_point=row["grade_point"],
                    result_status=row["result_status"],
                )
            )
        else:
            unmatched.append(row["raw_text"])

    return OcrResult(matches=matches, unmatched=unmatched)
