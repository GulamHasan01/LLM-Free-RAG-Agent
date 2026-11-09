from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    root_dir: Path = ROOT_DIR
    app_name: str = "LLM-Free RAG Retrieval Agent"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    collection_name: str = "documents"
    upload_dir: Path = ROOT_DIR / "data" / "uploads"
    chroma_path: Path = ROOT_DIR / "data" / "chroma_db"
    chunk_size: int = 700
    chunk_overlap: int = 120
    max_upload_mb: int = 20

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.chroma_path.mkdir(parents=True, exist_ok=True)
