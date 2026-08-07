from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ai.rag_system import add_document

router = APIRouter(prefix="/api/documents", tags=["Documents"])

class DocumentUpload(BaseModel):
    doc_id: str
    content: str

@router.post("/")
def upload_document(doc_data: DocumentUpload):
    try:
        result = add_document(doc_data.doc_id, doc_data.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))