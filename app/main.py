from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import documents, search
from app.core.config import settings
from app.services.embedding_service import EmbeddingService
from app.database.vector_store import VectorStore
from app.services.document_service import DocumentService
from app.services.retrieval_service import RetrievalService
# lifespan function is an asynchronous context manager that initializes the services required for the FastAPI application.
# It creates instances of the EmbeddingService, VectorStore, DocumentService, and RetrievalService using the configuration settings.
# These instances are then stored in the application's state for later use. The function yields control back to the FastAPI
# application, allowing it to run with the initialized services.
@asynccontextmanager
async def lifespan(app: FastAPI):
    embedding_service = EmbeddingService(settings.embedding_model)
    vector_store = VectorStore(settings.chroma_path, settings.collection_name)
    app.state.document_service = DocumentService(
        embedding_service, vector_store, settings.upload_dir
    )
    app.state.retrieval_service = RetrievalService(embedding_service, vector_store)
    yield

app = FastAPI(
    title="Fieldnotes – LLM-Free Semantic Document Retrieval System",
    description="LLM-free semantic document retrieval using embeddings and vector search.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(search.router, prefix="/search", tags=["Search"])

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "llm_enabled": False}

# Serve the lightweight browser UI from the same origin as the API.
FRONTEND_DIR = settings.root_dir / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
