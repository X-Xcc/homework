from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.core.legal_db import legal_db
from app.core.vector_store import vector_store
from app.models.schemas import LawArticle

router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("/law", response_model=List[LawArticle])
async def search_law(
    q: str = Query(..., description="搜索关键词"),
    type: Optional[str] = Query(None, description="法律类型: criminal/civil"),
    limit: int = Query(20, ge=1, le=100)
):
    results = legal_db.search(q, law_type=type, limit=limit)
    return results

@router.get("/law/{article_id}", response_model=LawArticle)
async def get_law_article(article_id: str):
    article = legal_db.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="法条未找到")
    return article

@router.get("/similar")
async def search_similar(
    q: str = Query(..., description="搜索内容"),
    limit: int = Query(5, ge=1, le=20)
):
    results = vector_store.search_similar(q, n_results=limit)
    return {"results": results}
