from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)

class SearchResult(BaseModel):
    content: str
    source: str | None = None
    page: int | None = None
    document_id: str
    chunk_index: int
    similarity_score: float

class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    llm_used: bool = False
