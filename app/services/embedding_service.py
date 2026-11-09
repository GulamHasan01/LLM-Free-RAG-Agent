from sentence_transformers import SentenceTransformer

class EmbeddingService:
    """Creates dense semantic vectors locally; this is not a generative LLM."""
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            texts, normalize_embeddings=True, convert_to_numpy=True
        )
        return vectors.tolist()

    def embed_query(self, query: str) -> list[float]:
        vector = self.model.encode(
            [query], normalize_embeddings=True, convert_to_numpy=True
        )[0]
        return vector.tolist()
