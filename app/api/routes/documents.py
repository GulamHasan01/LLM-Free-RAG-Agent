from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from app.schemas.document import DocumentUploadResponse, DocumentListResponse

router = APIRouter()
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(request: Request, file: UploadFile = File(...)):
    filename = file.filename or "uploaded_file"
    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Supported formats: PDF, TXT, DOCX")
    content = await file.read()
    if not content:
        raise HTTPException(400, "Uploaded file is empty")
    max_bytes = request.app.state.document_service.max_upload_bytes
    if len(content) > max_bytes:
        raise HTTPException(413, "File exceeds the configured upload size limit")
    try:
        return request.app.state.document_service.ingest(filename, content)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

@router.get("", response_model=DocumentListResponse)
def list_documents(request: Request):
    return {"documents": request.app.state.document_service.list_documents()}

@router.get("/{document_id}")
def get_document(document_id: str, request: Request):
    document = request.app.state.document_service.get_document(document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    return document

@router.delete("/{document_id}")
def delete_document(document_id: str, request: Request):
    deleted = request.app.state.document_service.delete_document(document_id)
    if not deleted:
        raise HTTPException(404, "Document not found")
    return {"deleted": True, "document_id": document_id}
