import sys

import pytest


@pytest.fixture
def _patched_vector_store(monkeypatch):
    """绕开真实 chromadb 启动开销。"""
    ai_mod = sys.modules["app.core.vector_store"]

    def fake_search(self, query, n_results=5):
        return []

    monkeypatch.setattr(ai_mod.VectorStore, "search_similar", fake_search)


@pytest.mark.asyncio
async def test_search_law_keyword(client):
    resp = await client.get("/api/search/law?q=合同")
    assert resp.status_code == 200
    # 即便数据为空，结构也应该是 list
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_search_similar(client, _patched_vector_store):
    resp = await client.get("/api/search/similar?q=违约&limit=3")
    assert resp.status_code == 200
    body = resp.json()
    assert "results" in body


@pytest.mark.asyncio
async def test_templates_list(client):
    resp = await client.get("/api/templates")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_templates_categories(client):
    resp = await client.get("/api/templates/categories/list")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

