import chromadb
import json
import numpy as np
import pickle
from pathlib import Path
from chromadb.config import Settings as ChromaSettings
from chromadb.api.types import EmbeddingFunction, Embeddings
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Optional, Dict, Any
from app.config import settings


class ChineseTFIDFEmbedding(EmbeddingFunction):
    """TF-IDF based embedding for Chinese legal text. No external downloads needed."""

    def __init__(self, persist_dir: str):
        self.persist_dir = Path(persist_dir)
        self.state_path = self.persist_dir / "tfidf_vectorizer.pkl"
        self.vectorizer: Optional[TfidfVectorizer] = None
        self._fitted = False
        self._load()

    def _load(self):
        if self.state_path.exists():
            try:
                with open(self.state_path, "rb") as f:
                    self.vectorizer = pickle.load(f)
                self._fitted = True
            except Exception:
                self.vectorizer = None
                self._fitted = False

    def _save(self):
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "wb") as f:
            pickle.dump(self.vectorizer, f)

    def fit(self, documents: List[str]):
        self.vectorizer = TfidfVectorizer(
            max_features=384,
            analyzer="char",
            ngram_range=(2, 4),
            sublinear_tf=True,
        )
        self.vectorizer.fit(documents)
        self._fitted = True
        self._save()

    def __call__(self, input: List[str]) -> Embeddings:
        if not self._fitted or self.vectorizer is None:
            # Fallback: zero vectors
            return [[0.0] * 384 for _ in input]
        vectors = self.vectorizer.transform(input).toarray()
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        vectors = vectors / norms
        return vectors.tolist()


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        self.ef = ChineseTFIDFEmbedding(persist_dir=settings.CHROMA_PERSIST_DIR)
        self._init_collection()

    def _init_collection(self):
        """Initialize collection, auto-fixing schema mismatches."""
        try:
            self.law_collection = self.client.get_collection(
                name="law_articles",
                embedding_function=self.ef,
            )
            if not self.ef._fitted and self.law_collection.count() > 0:
                docs_data = self.law_collection.get(include=["documents"])
                if docs_data and docs_data["documents"]:
                    self.ef.fit(docs_data["documents"])
        except Exception:
            # Collection may use old embedding function; recreate
            try:
                self.client.delete_collection("law_articles")
            except Exception:
                pass
            self.law_collection = self.client.get_or_create_collection(
                name="law_articles",
                embedding_function=self.ef,
                metadata={"hnsw:space": "cosine"},
            )

    def _sanitize_metadata(self, meta: dict) -> dict:
        sanitized = {}
        for k, v in meta.items():
            if isinstance(v, list):
                sanitized[k] = ", ".join(str(x) for x in v)
            elif isinstance(v, dict):
                sanitized[k] = json.dumps(v, ensure_ascii=False)
            elif v is None:
                sanitized[k] = ""
            else:
                sanitized[k] = str(v) if not isinstance(v, (str, int, float, bool)) else v
        return sanitized

    def search_similar(
        self,
        query: str,
        n_results: int = 5,
        category: Optional[str] = None,
    ) -> List[dict]:
        where_filter = None
        if category:
            where_filter = {"category": category}

        results = self.law_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
        )

        items = []
        if results and results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                items.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "metadata": self._deserialize_metadata(meta),
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                })
        return items

    def _deserialize_metadata(self, meta: dict) -> dict:
        if not meta:
            return {}
        result: Dict[str, Any] = dict(meta)
        list_fields = ["applicable_scenarios", "keywords", "judicial_interpretations", "related_cases"]
        for field in list_fields:
            if field in result and isinstance(result[field], str):
                val = result[field].strip()
                if val:
                    result[field] = [x.strip() for x in val.split(", ")]
                else:
                    result[field] = []
        return result

    def initialize_law_data(self, articles: List[dict]):
        """Batch-import structured law articles into ChromaDB with full metadata."""
        try:
            self.client.delete_collection("law_articles")
        except Exception:
            pass

        self.law_collection = self.client.get_or_create_collection(
            name="law_articles",
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"},
        )

        ids = []
        documents = []
        metadatas = []

        for a in articles:
            ids.append(a["id"])
            doc = (
                f"{a.get('law_name', '')} {a.get('article_number', '')} "
                f"{a.get('title', '')}: {a['content']}"
            )
            documents.append(doc)

            meta = {
                "law_name": a.get("law_name", ""),
                "article_number": a.get("article_number", ""),
                "category": a.get("category", ""),
                "chapter": a.get("chapter", ""),
                "title": a.get("title", ""),
                "applicable_scenarios": a.get("applicable_scenarios", []),
                "keywords": a.get("keywords", []),
                "judicial_interpretations": a.get("judicial_interpretations", []),
            }
            metadatas.append(self._sanitize_metadata(meta))

        print("  Fitting TF-IDF vectorizer on all documents...")
        self.ef.fit(documents)

        batch_size = 20
        total = 0
        for i in range(0, len(ids), batch_size):
            self.law_collection.upsert(
                ids=ids[i:i + batch_size],
                documents=documents[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
            )
            total += min(batch_size, len(ids) - i)
            print(f"  Imported {total}/{len(ids)} articles...")

        return total

    def count(self) -> int:
        return self.law_collection.count()

    def list_categories(self) -> List[str]:
        results = self.law_collection.get(include=["metadatas"])
        categories = set()
        if results and results["metadatas"]:
            for m in results["metadatas"]:
                cat = m.get("category", "")
                if cat:
                    categories.add(cat)
        return sorted(categories)


vector_store = VectorStore()
