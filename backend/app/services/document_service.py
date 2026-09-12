from typing import Any, Dict

from app.services.ocr_service import extract_text
from app.services.ai_extraction_service import extract_document_data
from app.services.financial_validation_service import validate_financial_data


def process_document(
    file_path: str,
    document_type: str,
) -> Dict[str, Any]:
    """
    Complete document intelligence pipeline:

    File
      ↓
    OCR/Text Extraction
      ↓
    AI Structured Extraction
      ↓
    Financial Validation
    """

    # --------------------------------------------------
    # STEP 1: OCR / TEXT EXTRACTION
    # --------------------------------------------------

    ocr_result = extract_text(file_path)

    if not ocr_result["success"]:
        return {
            "processing_status": "FAILED",
            "extracted_text": "",
            "pages": [],
            "extracted_data": {},
            "validation": {
                "overall_status": "FAILED",
                "errors": [
                    ocr_result.get("error", "Document extraction failed")
                ]
            }
        }

    document_text = ocr_result["text"]

    if not document_text.strip():
        return {
            "processing_status": "FAILED",
            "extracted_text": "",
            "pages": ocr_result.get("pages", []),
            "extracted_data": {},
            "validation": {
                "overall_status": "FAILED",
                "errors": ["No text could be extracted from document"]
            }
        }

    # --------------------------------------------------
    # STEP 2: AI EXTRACTION
    # --------------------------------------------------

    ai_result = extract_document_data(
        document_text=document_text,
        document_type=document_type,
    )

    if not ai_result["success"]:
        return {
            "processing_status": "AI_EXTRACTION_FAILED",
            "extracted_text": document_text,
            "pages": ocr_result.get("pages", []),
            "extracted_data": {},
            "validation": {
                "overall_status": "SKIPPED",
                "errors": [ai_result.get("error", "AI extraction failed")]
            }
        }

    extracted_data = ai_result["data"]

    # --------------------------------------------------
    # STEP 3: FINANCIAL VALIDATION
    # --------------------------------------------------

    validation = validate_financial_data(
        document_type=document_type,
        data=extracted_data,
    )

    # --------------------------------------------------
    # STEP 4: FINAL RESULT
    # --------------------------------------------------

    if validation["overall_status"] in {"PASS", "SKIPPED"}:
        processing_status = "PASS"
    else:
        processing_status = "FAILED"

    return {
        "processing_status": processing_status,
        "extracted_text": document_text,
        "pages": ocr_result.get("pages", []),
        "extracted_data": extracted_data,
        "validation": validation,
    }