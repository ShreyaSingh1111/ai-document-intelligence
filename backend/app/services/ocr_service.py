from pathlib import Path

import fitz
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def _ocr_pdf_page(page) -> str:
    pix = page.get_pixmap(dpi=300)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return pytesseract.image_to_string(img).strip()


def extract_text(file_path: str) -> dict:
    path = Path(file_path)

    if path.suffix.lower() == ".pdf":
        try:
            document = fitz.open(path)

            pages = []
            full_text = ""

            for page_number, page in enumerate(document, start=1):
                text = page.get_text("text").strip()

                if len(text) < 20:
                    text = _ocr_pdf_page(page)

                pages.append({
                    "page_number": page_number,
                    "text": text
                })

                full_text += f"\n--- Page {page_number} ---\n{text}"

            document.close()

            extracted_text = full_text.strip()

            return {
                "success": True,
                "text": extracted_text,
                "pages": pages,
                "ocr_required": len(extracted_text) < 20
            }

        except Exception as e:
            return {
                "success": False,
                "text": "",
                "pages": [],
                "error": str(e)
            }

    if path.suffix.lower() in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        try:
            image = Image.open(path)

            text = pytesseract.image_to_string(image).strip()

            return {
                "success": True,
                "text": text,
                "pages": [
                    {
                        "page_number": 1,
                        "text": text
                    }
                ],
                "image_mode": image.mode,
                "image_size": image.size,
                "ocr_required": False
            }

        except Exception as e:
            return {
                "success": False,
                "text": "",
                "pages": [],
                "error": str(e)
            }

    return {
        "success": False,
        "text": "",
        "pages": [],
        "error": f"Unsupported file type: {path.suffix}"
    }
