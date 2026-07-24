from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import OcrResult
from ..ocr_service import process_pdf

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("/upload", response_model=OcrResult)
async def upload_pdf(
    file: UploadFile = File(...),
    department: str = Form(default="AIDS"),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    result = process_pdf(pdf_bytes, db, department=department.upper())
    return result
