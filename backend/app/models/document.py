from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    document_name = Column(String(255), nullable=False, index=True)
    document_type = Column(String(100), nullable=False)

    file_path = Column(String(500), nullable=True)
    processing_status = Column(String(50), nullable=False)

    extracted_data = Column(Text, nullable=True)
    validation_data = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )