import hashlib
import uuid
from pathlib import Path
from app.processors.document_loader import extract_text
from app.processors.text_splitter import split_text

class DocumentService:
    def __init__(self, embedding_service, vector_store, upload_dir: Path):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.max_upload_bytes = 20 * 1024 * 1024
        self._documents = {}
#ingest method is responsible for processing and storing a document. It takes in the filename and content of the document,
#generates a unique document ID, and saves the file to the specified upload directory. The method then extracts text 
#from the document, splits it into chunks, and generates embeddings for each chunk using the embedding service. 
#The chunks, embeddings, and associated metadata are added to the vector store. If any errors occur during processing, 
#the stored file is deleted. Finally, a record of the document is created and stored in memory, and the method returns this record.
    def ingest(self, filename: str, content: bytes):
        suffix = Path(filename).suffix.lower()
        document_id = str(uuid.uuid4())
        safe_name = Path(filename).name
        stored_path = self.upload_dir / f"{document_id}{suffix}"
        stored_path.write_bytes(content)
        try:
            pages = extract_text(stored_path)
            chunks, metadata = [], []
            for page_number, page_text in pages:
                for chunk_index, chunk in enumerate(split_text(page_text)):
                    chunks.append(chunk)
                    metadata.append({
                        "document_id": document_id,
                        "source": safe_name,
                        "page": page_number,
                        "chunk_index": chunk_index,
                    })
            if not chunks:
                raise ValueError("No extractable text found in the document.")
            embeddings = self.embedding_service.embed_documents(chunks)
            ids = [f"{document_id}-{i}" for i in range(len(chunks))]
            self.vector_store.add(ids, chunks, embeddings, metadata)
        except Exception:
            stored_path.unlink(missing_ok=True)
            raise

        record = {
            "document_id": document_id,
            "filename": safe_name,
            "chunks": len(chunks),
            "pages_with_text": len(pages),
            "sha256": hashlib.sha256(content).hexdigest(),
        }
        self._documents[document_id] = {**record, "stored_path": str(stored_path)}
        return record

    def list_documents(self):
        return [
            {k: v for k, v in doc.items() if k != "stored_path"}
            for doc in self._documents.values()
        ]

    def get_document(self, document_id: str):
        doc = self._documents.get(document_id)
        if not doc:
            return None
        return {k: v for k, v in doc.items() if k != "stored_path"}

    def delete_document(self, document_id: str):
        doc = self._documents.get(document_id)
        if not doc:
            return False
        self.vector_store.delete_document(document_id)
        Path(doc["stored_path"]).unlink(missing_ok=True)
        del self._documents[document_id]
        return True
