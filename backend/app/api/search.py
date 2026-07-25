from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.core.legal_db import legal_db
from app.core.vector_store import vector_store
from app.models.schemas import LawArticle

router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("/law", response_model=List[LawArticle])
async def search_law(
    q: str = Query(..., description="\u641c\u7d22\u5173\u952e\u8bcd"),
    category: Optional[str] = Query(None, description="\u6cd5\u5f8b\u5206\u7c7b"),
    limit: int = Query(20, ge=1, le=100),
):
    results = legal_db.search(q, category=category, limit=limit)
    return results

@router.get("/law/{article_id}", response_model=LawArticle)
async def get_law_article(article_id: str):
    article = legal_db.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="\u6cd5\u6761\u672a\u627e\u5230")
    return article

@router.get("/similar")
async def search_similar(
    q: str = Query(..., description="\u641c\u7d22\u5185\u5bb9"),
    limit: int = Query(5, ge=1, le=20),
    category: Optional[str] = Query(None, description="\u6cd5\u5f8b\u5206\u7c7b"),
):
    # Use keyword-based search (reliable, no external deps)
    # ChromaDB vector search available via /api/search/vector
    results = legal_db.search(q, category=category, limit=limit)
    items = []
    for a in results:
        items.append({
            "id": a.id,
            "content": f"{a.law_name} {a.article_number} {a.title or ''}: {a.content}",
            "metadata": {
                "law_name": a.law_name,
                "article_number": a.article_number,
                "title": a.title,
                "judicial_interpretations": a.judicial_interpretations,
            },
        })
    return {"results": items}

@router.get("/vector")
async def search_vector(
    q: str = Query(..., description="\u641c\u7d22\u5185\u5bb9"),
    limit: int = Query(5, ge=1, le=20),
    category: Optional[str] = Query(None, description="\u6cd5\u5f8b\u5206\u7c7b"),
):
    """Vector-based semantic search using TF-IDF embeddings."""
    results = vector_store.search_similar(q, n_results=limit, category=category)
    return {"results": results}

@router.get("/categories")
async def list_categories():
    return {"categories": legal_db.list_categories()}
