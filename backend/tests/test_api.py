import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_reject_unsupported_file_type():
    file_content = io.BytesIO(b"just some text content")
    response = client.post(
        "/documents/upload?document_type=invoice",
        files={"file": ("test.txt", file_content, "text/plain")},
    )
    assert response.status_code == 400


def test_reject_empty_file():
    file_content = io.BytesIO(b"")
    response = client.post(
        "/documents/upload?document_type=invoice",
        files={"file": ("empty.pdf", file_content, "application/pdf")},
    )
    assert response.status_code == 400


def test_list_documents_endpoint():
    response = client.get("/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
