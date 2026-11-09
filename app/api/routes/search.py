from fastapi import APIRouter, HTTPException, Request
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter()

@router.post("", response_model=SearchResponse)
def search_documents(payload: SearchRequest, request: Request):
    if not payload.query.strip():
        raise HTTPException(400, "Query cannot be empty")
    results = request.app.state.retrieval_service.search(payload.query, payload.top_k)
    return {"query": payload.query, "results": results, "llm_used": False}
