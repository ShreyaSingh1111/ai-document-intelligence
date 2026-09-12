from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.documents import router as document_router
from app.core.database import Base, engine

from app.models.document import Document


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Intelligence API",
    description="AI-powered financial document extraction and validation system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "document-intelligence-api",
    }


app.include_router(document_router)

app.mount("/", StaticFiles(directory="../frontend/templates", html=True), name="frontend")
