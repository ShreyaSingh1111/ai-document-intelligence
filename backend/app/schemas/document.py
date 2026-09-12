from pydantic import BaseModel
from typing import Any, Optional


class DocumentResponse(BaseModel):
    document_name: str
    document_type: str
    status: str
    extracted_data: Optional[Any] = None
    validation_results: Optional[Any] = None
    issues: Optional[Any] = None