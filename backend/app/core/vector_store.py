import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Optional
from app.config import settings

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.law_collection = self.client.get_or_create_collection(
            name="law_articles",
            metadata={"hnsw:space": "cosine"}
        )

    def add_law_article(self, article_id: str, content: str, metadata: dict = None):
        self.law_collection.upsert(
            ids=[article_id],
            documents=[content],
            metadatas=[metadata or {}]
        )

    def search_similar(self, query: str, n_results: int = 5) -> List[dict]:
        results = self.law_collection.query(
            query_texts=[query],
            n_results=n_results
        )

        items = []
        if results and results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                items.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0
                })

        return items

    def initialize_law_data(self, articles: List[dict]):
        ids = [a["id"] for a in articles]
        documents = [f"{a.get('title', '')} {a['content']}" for a in articles]
        metadatas = [{"law_name": a.get("law_name", ""), "article_number": a.get("article_number", "")} for a in articles]

        batch_size = 100
        for i in range(0, len(ids), batch_size):
            self.law_collection.upsert(
                ids=ids[i:i+batch_size],
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )

vector_store = VectorStore()
