from pathlib import Path
import chromadb

class VectorStore:
    def __init__(self, persist_path: Path, collection_name: str):
        client = chromadb.PersistentClient(path=str(persist_path))
        self.collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},#hnsw Hierarchical Navigable Small World. algo is used for efficient similarity search in high-dimensional spaces,
            # and "cosine" specifies that cosine similarity will be used as the distance metric for comparing vectors.
        )

    def add(self, ids, documents, embeddings, metadatas):
        self.collection.add(
            ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
        )
# query method is used to retrieve the most similar documents from the vector store based on a given query embedding. 
#It takes in a query embedding and the number of top results to return (top_k). The method first checks if the collection is empty; if it is, it returns an empty list. Otherwise, it performs a query on the collection using the provided query embedding and retrieves the specified number of results. The results include the documents, their associated metadata, and the distances (similarity scores) between the query embedding and the retrieved documents. The method then constructs a list of dictionaries containing the document, metadata, and distance for each result and returns this list.
    def query(self, query_embedding, top_k: int):
        if self.collection.count() == 0:
            return []
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        items = []
        for i in range(len(result["ids"][0])):
            items.append({
                "document": result["documents"][0][i],
                "metadata": result["metadatas"][0][i],
                "distance": result["distances"][0][i],
            })
        return items

    def delete_document(self, document_id: str):
        self.collection.delete(where={"document_id": document_id})
