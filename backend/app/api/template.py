from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import json
from pathlib import Path

router = APIRouter(prefix="/api/templates", tags=["templates"])

TEMPLATES_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "templates.json"

def load_templates():
    try:
        with open(TEMPLATES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

@router.get("")
async def list_templates(category: Optional[str] = None, keyword: Optional[str] = Query(None)):
    templates = load_templates()
    if category:
        templates = [t for t in templates if t.get("category") == category]
    if keyword:
        keyword_normalized = keyword.strip().lower()
        templates = [
            t for t in templates
            if keyword_normalized in t.get("name", "").lower()
            or keyword_normalized in t.get("description", "").lower()
            or keyword_normalized in t.get("category", "").lower()
        ]
    return templates

@router.get("/categories/list")
async def list_categories():
    templates = load_templates()
    categories = sorted({t.get("category", "") for t in templates if t.get("category")})
    return categories


@router.get("/{template_id}")
async def get_template(template_id: str):
    templates = load_templates()
    for t in templates:
        if t["id"] == template_id:
            return t
    raise HTTPException(status_code=404, detail="模板未找到")
