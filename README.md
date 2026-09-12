# AI Document Intelligence Platform

AI-powered system for extracting, validating and presenting financial
document data (invoices, balance sheets, profit & loss statements, cash
flow statements) from PDF/JPG/PNG uploads.

## 1. Solution Overview & Architecture

Flow: Upload -> File Validation -> OCR/Text Extraction -> AI Structured
Extraction -> Financial Validation -> Persistence -> Dashboard/API.

Frontend (HTML/CSS/JS) -> FastAPI Backend -> SQLite database.

Backend layers:
- api/routes/documents.py (REST endpoints)
- services/document_service.py (pipeline orchestration)
- services/ocr_service.py (PyMuPDF text + Tesseract OCR fallback)
- services/ai_extraction_service.py (Groq LLM structured extraction)
- services/financial_validation_service.py (rule-based checks)
- models/document.py (SQLAlchemy model)
- core/database.py (SQLite connection)

## 2. Technology Stack

- Backend: FastAPI + SQLAlchemy + SQLite
- OCR/Text extraction: PyMuPDF (native PDF text) with Tesseract OCR
  fallback for scanned/image-based PDFs and images
- AI extraction: Groq (openai/gpt-oss-20b model) for structured JSON
  field/table extraction
- Financial validation: custom rule-based Python checks (deterministic,
  no LLM involved)
- Frontend: plain HTML/CSS/JavaScript, calling the backend REST API
- Testing: pytest

## 3. Local Setup

cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

Install Tesseract OCR system binary:
- Windows: winget install --id UB-Mannheim.TesseractOCR -e
- Linux: sudo apt-get install tesseract-ocr

Create backend/.env (see .env.example).

Run: python -m uvicorn app.main:app --reload
Open frontend/templates/dashboard.html in a browser.
Swagger docs: http://127.0.0.1:8000/docs

## 4. Environment Variables

GROQ_API_KEY=your_groq_api_key_here

## 5. Deployed URLs

- Frontend: https://ai-document-intelligence-bg01.onrender.com
- Backend API: https://ai-document-intelligence-bg01.onrender.com
- Swagger/OpenAPI: https://ai-document-intelligence-bg01.onrender.com/docs
- GitHub repository: https://github.com/ShreyaSingh1111/ai-document-intelligence

## 6. API Examples

POST /documents/upload
curl -X POST "http://127.0.0.1:8000/documents/upload?document_type=invoice" -F "file=@invoice.pdf;type=application/pdf"

GET /documents/by-name/{document_name}
curl "http://127.0.0.1:8000/documents/by-name/invoice.pdf"

GET /documents
curl "http://127.0.0.1:8000/documents"

## 7. OCR / LLM Services Used

OCR: PyMuPDF for native text extraction; Tesseract OCR (open-source,
local, free) as fallback for scanned PDFs/images.
LLM: Groq API, openai/gpt-oss-20b model, free tier, used only for
structured extraction, never for financial calculations.

## 8. Financial Validation Rules & Tolerance

Tolerance: 0.01 absolute difference before a check is marked FAIL.

- Invoice: subtotal + tax_amount - discount = total_amount; per line
  item quantity x unit_price = amount; sum of line items reconciles
  to subtotal.
- Balance sheet: total_liabilities + total_equity = total_assets.
- Profit & Loss: revenue - cost_of_sales = gross_profit;
  gross_profit - operating_expenses = operating_profit.
- Cash flow: operating + investing + financing = net_change_in_cash;
  opening_cash + net_change_in_cash = closing_cash.

Missing required fields return SKIPPED rather than assuming a value.

## 9. Database / Persistence

SQLite (documents.db), single documents table storing name, type,
file path, processing status, and JSON-serialized extracted data and
validation results. GET /documents/by-name/{name} returns the latest
row for that name.

## 10. Known Limitations

- OCR accuracy depends on scan quality; no image pre-processing.
- No authentication/authorization on the API.
- No automated document-type classification (by design, per scope).
- No confidence scoring implemented.
- Duplicate uploads create new rows rather than explicit versioning.

## 11. What I Would Change for Production

- Add authentication and per-user document scoping.
- Move from SQLite to PostgreSQL for concurrent access.
- Add image pre-processing before OCR.
- Add structured logging/observability and retry/backoff around the
  Groq API call.
- Containerize with a proper CI/CD pipeline.
- Add confidence scoring based on OCR quality metrics.

## 12. AI Coding Assistants Used

Claude (Anthropic) was used throughout development for debugging
import/circular-dependency errors, writing the OCR fallback logic,
CORS configuration, REST endpoint implementation, the frontend
dashboard, pytest test cases, and this README.
