from pathlib import Path

import fitz


ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
ALLOWED_DOCUMENT_TYPES = {
    "invoice",
    "balance_sheet",
    "profit_and_loss",
    "cash_flow_statement",
}


def validate_document(file_path: str, document_type: str) -> dict:
    path = Path(file_path)

    # Check document type
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        return {
            "valid": False,
            "error": f"Unsupported document type: {document_type}",
        }

    # Check file extension
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return {
            "valid": False,
            "error": "Unsupported file format. Use PDF, JPG, JPEG, or PNG.",
        }

    # Check file exists and is not empty
    if not path.exists() or path.stat().st_size == 0:
        return {
            "valid": False,
            "error": "File is missing or empty.",
        }

    # PDF validation
    if path.suffix.lower() == ".pdf":
        try:
            document = fitz.open(path)

            page_count = len(document)

            if page_count == 0:
                document.close()
                return {
                    "valid": False,
                    "error": "PDF contains no pages.",
                }

            if page_count > 3:
                document.close()
                return {
                    "valid": False,
                    "error": "Document must contain a maximum of 3 pages.",
                }

            document.close()

            return {
                "valid": True,
                "page_count": page_count,
                "file_type": "pdf",
            }

        except Exception:
            return {
                "valid": False,
                "error": "PDF is corrupted or cannot be opened.",
            }

    # Image validation
    try:
        from PIL import Image

        image = Image.open(path)
        image.verify()

        return {
            "valid": True,
            "page_count": 1,
            "file_type": "image",
        }

    except Exception:
        return {
            "valid": False,
            "error": "Image is corrupted or cannot be opened.",
        }