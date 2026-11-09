class RetrievalService:
    def __init__(self, embedding_service, vector_store):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def search(self, query: str, top_k: int = 5):
        query_vector = self.embedding_service.embed_query(query)
        matches = self.vector_store.query(query_vector, top_k)
        results = []
        for item in matches:
            # Chroma returns cosine distance when cosine space is configured.
            similarity = max(0.0, min(1.0, 1.0 - float(item["distance"])))
            results.append({
                "content": item["document"],
                "source": item["metadata"].get("source"),
                "page": item["metadata"].get("page"),
                "document_id": item["metadata"].get("document_id"),
                "chunk_index": item["metadata"].get("chunk_index"),
                "similarity_score": round(similarity, 4),
            })
        return results
