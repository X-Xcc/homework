#!/usr/bin/env python3
"""import_to_vectordb.py - Load all knowledge_base JSONs into ChromaDB vector store."""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.core.vector_store import vector_store

KB_DIR = Path(__file__).resolve().parents[1] / "backend" / "data" / "knowledge_base"

CATEGORY_MAP = {
    "civil_foundation.json": "\u6c11\u6cd5\u57fa\u7840",
    "ai_compliance.json": "AI\u8fd0\u8425\u5408\u89c4",
    "data_security.json": "\u6570\u636e\u5b89\u5168",
    "commercial.json": "\u5546\u4e8b\u6cd5\u89c4",
    "industry_specific.json": "\u884c\u4e1a\u4e13\u9879",
    "criminal_risk.json": "\u5211\u4e8b\u98ce\u9669",
    "foreign_compliance.json": "\u6d89\u5916\u6cd5\u89c4",
}

def main():
    print("=" * 60)
    print("Legal Knowledge Base \u2192 ChromaDB Vector Import")
    print("=" * 60)

    all_articles = []
    for filename, category in CATEGORY_MAP.items():
        filepath = KB_DIR / filename
        if not filepath.exists():
            print(f"  SKIP: {filename} not found")
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            articles = json.load(f)
        for a in articles:
            if "category" not in a or not a["category"]:
                a["category"] = category
        all_articles.extend(articles)
        print(f"  Loaded {filename}: {len(articles)} articles")

    print(f"\nTotal articles to import: {len(all_articles)}")

    # Validate
    empty_content = [a["id"] for a in all_articles if not a.get("content", "").strip()]
    if empty_content:
        print(f"  WARNING: {len(empty_content)} articles with empty content: {empty_content}")

    # Import
    count = vector_store.initialize_law_data(all_articles)
    print(f"\nImported into ChromaDB: {count} articles")

    # Verify
    db_count = vector_store.count()
    print(f"ChromaDB collection count: {db_count}")
    categories = vector_store.list_categories()
    print(f"Categories: {categories}")

    # Test search
    test_queries = [
        "\u683c\u5f0f\u6761\u6b3e\u65e0\u6548",
        "\u4e2a\u4eba\u4fe1\u606f\u4fdd\u62a4",
        "\u5408\u540c\u8bc8\u9a97",
        "GDPR",
    ]
    print("\nTest search results:")
    for q in test_queries:
        results = vector_store.search_similar(q, n_results=2)
        print(f"\n  Query: {q}")
        for r in results:
            meta = r["metadata"]
            print(f"    - [{meta.get('category', '')}] {meta.get('law_name', '')} "
                  f"{meta.get('article_number', '')} {meta.get('title', '')} "
                  f"(dist: {r['distance']:.4f})")

    print(f"\nDone. Vector store ready at: {'D:/homework/backend/data/vector_db'}")

if __name__ == "__main__":
    main()
