from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap,
    separators=["\\n\\n", "\\n", ". ", " ", ""],
)

def split_text(text: str) -> list[str]:
    return [chunk.strip() for chunk in _splitter.split_text(text) if chunk.strip()]
