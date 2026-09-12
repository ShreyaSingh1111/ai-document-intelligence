import json
import logging
from pathlib import Path

import fitz
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.services.document_service import process_document


logger = logging.getLogger("documents")

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_PAGES = 3


@router.get("/health")
def document_health():
    return {
        "status": "ok",
        "service": "document intelligence"
    }


@router.get("")
def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).order_by(desc(Document.created_at)).all()

    return [
        {
            "document_id": d.id,
            "document_name": d.document_name,
            "document_type": d.document_type,
            "processing_status": d.processing_status,
            "created_at": d.created_at,
        }
        for d in documents
    ]


@router.get("/by-name/{document_name}")
def get_document_by_name(document_name: str, db: Session = Depends(get_db)):
    document = (
        db.query(Document)
        .filter(Document.document_name == document_name)
        .order_by(desc(Document.created_at))
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document_id": document.id,
        "document_name": document.document_name,
        "document_type": document.document_type,
        "processing_status": document.processing_status,
        "extracted_data": json.loads(document.extracted_data) if document.extracted_data else {},
        "validation": json.loads(document.validation_data) if document.validation_data else {},
        "created_at": document.created_at,
    }


def _validate_file(file_path: Path, extension: str) -> None:
    """Validate file integrity, type and page count before processing."""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}. Only PDF, JPG, PNG are supported."
        )

    if file_path.stat().st_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if extension == ".pdf":
        try:
            document = fitz.open(file_path)
            page_count = document.page_count
            document.close()
        except Exception:
            raise HTTPException(status_code=400, detail="Uploaded PDF is corrupted or unreadable.")

        if page_count == 0:
            raise HTTPException(status_code=400, detail="Uploaded PDF has no pages.")

        if page_count > MAX_PAGES:
            raise HTTPException(
                status_code=400,
                detail=f"Document exceeds the maximum of {MAX_PAGES} pages (found {page_count})."
            )


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = "invoice",
    db: Session = Depends(get_db),
):
    extension = Path(file.filename).suffix.lower()
    file_path = UPLOAD_DIR / file.filename

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    try:
        _validate_file(file_path, extension)
    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise

    document = Document(
        document_name=file.filename,
        document_type=document_type,
        file_path=str(file_path),
        processing_status="PROCESSING",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        result = process_document(
            file_path=str(file_path),
            document_type=document_type,
        )
    except Exception as e:
        logger.exception("Processing failed for document_id=%s", document.id)
        document.processing_status = "FAILED"
        document.validation_data = json.dumps({"overall_status": "FAILED", "issues": [str(e)]})
        db.commit()
        raise HTTPException(status_code=500, detail="Document processing failed. Please try again.")

    document.processing_status = result["processing_status"]
    document.extracted_data = json.dumps(result.get("extracted_data", {}), default=str)
    document.validation_data = json.dumps(result.get("validation", {}), default=str)

    db.commit()
    db.refresh(document)

    return {
        "document_id": document.id,
        "document_name": document.document_name,
        "document_type": document.document_type,
        "processing_status": document.processing_status,
        "extracted_data": result.get("extracted_data", {}),
        "validation": result.get("validation", {}),
        "pages": result.get("pages", []),
    }
