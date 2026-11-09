from pydantic import BaseModel

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks: int
    pages_with_text: int
    sha256: str

class DocumentListResponse(BaseModel):
    documents: list[DocumentUploadResponse]
