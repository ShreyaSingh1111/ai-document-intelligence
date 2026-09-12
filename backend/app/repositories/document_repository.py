import json

from sqlalchemy.orm import Session

from app.models.document import Document


def create_document(
    db: Session,
    document_name: str,
    document_type: str,
    file_path: str,
    processing_status: str,
    extracted_data: dict | None = None,
    validation_data: dict | None = None,
):
    document = Document(
        document_name=document_name,
        document_type=document_type,
        file_path=file_path,
        processing_status=processing_status,
        extracted_data=json.dumps(extracted_data) if extracted_data else None,
        validation_data=json.dumps(validation_data) if validation_data else None,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_document_by_name(
    db: Session,
    document_name: str,
):
    return (
        db.query(Document)
        .filter(Document.document_name == document_name)
        .first()
    )


def get_all_documents(db: Session):
    return (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )