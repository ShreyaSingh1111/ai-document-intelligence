from pydantic import BaseModel
from typing import Any, Optional


class Evidence(BaseModel):
    source_text: Optional[str] = None
    page_number: Optional[int] = None


class ExtractedField(BaseModel):
    value: Any = None
    evidence: Optional[Evidence] = None


class ExtractionResult(BaseModel):
    fields: dict[str, ExtractedField] = {}
    tables: list[dict[str, Any]] = []