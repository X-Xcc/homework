import io
import sys

import pytest

from app.core.security import create_access_token


@pytest.fixture
def _patched_pipeline(monkeypatch):
    """mock 文档解析与 AI 分析，绕开真实 OCR / MiMo。"""
    doc_mod = sys.modules["app.core.document_service"]
    ai_mod = sys.modules["app.core.ai_analyzer"]

    # 文档解析：返回固定文本
    def fake_validate(path, max_size):
        return True, "ok"

    def fake_parse(path):
        return "合同全文：甲方 / 乙方 / 金额 / 期限 / 违约责任..."

    monkeypatch.setattr(doc_mod.document_parser, "validate_file", fake_validate)
    monkeypatch.setattr(doc_mod.document_parser, "parse", fake_parse)

    # AI 分析：返回固定 JSON
    async def fake_analyze(text):
        return {
            "risks": [
                {
                    "level": "high",
                    "title": "违约责任不清",
                    "description": "...",
                    "location": "第5条",
                    "legal_basis": ["民法典第584条"],
                    "suggestion": "...",
                },
            ],
            "summary": "测试总结",
            "overall_risk_level": "high",
            "overall_score": 75,
        }

    monkeypatch.setattr(ai_mod.ai_analyzer, "analyze_contract", fake_analyze)

    async def fake_compare(text_a, text_b):
        return {
            "changes": [
                {"type": "modify", "original": "A", "modified": "B", "location": "第1条"},
            ],
            "summary": "测试对比",
        }

    monkeypatch.setattr(ai_mod.ai_analyzer, "compare_documents", fake_compare)


def _auth_headers(user):
    token = create_access_token(user.id, user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_analyze_then_get(client, normal_user, _patched_pipeline):
    headers = _auth_headers(normal_user)

    # 上传分析
    files = {"file": ("contract.txt", io.BytesIO(b"fake contract"), "text/plain")}
    resp = await client.post("/api/document/analyze", files=files, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    assert body["overall_risk_level"] == "high"
    assert isinstance(body["risks"], list)
    assert len(body["risks"]) >= 1

    # 查询分析结果
    analysis_id = body["id"]
    resp = await client.get(f"/api/document/analysis/{analysis_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == analysis_id


@pytest.mark.asyncio
async def test_compare_documents(client, normal_user, _patched_pipeline):
    headers = _auth_headers(normal_user)
    files = {
        "file_a": ("a.txt", io.BytesIO(b"v1"), "text/plain"),
        "file_b": ("b.txt", io.BytesIO(b"v2"), "text/plain"),
    }
    resp = await client.post("/api/document/compare", files=files, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    assert isinstance(body["changes"], list)


@pytest.mark.asyncio
async def test_analyze_rejects_oversize(client, normal_user, monkeypatch):
    import sys

    doc_mod = sys.modules["app.core.document_service"]

    def reject(_path, _size):
        return False, "too big"

    monkeypatch.setattr(doc_mod.document_parser, "validate_file", reject)

    headers = _auth_headers(normal_user)
    files = {"file": ("x.txt", io.BytesIO(b"x"), "text/plain")}
    resp = await client.post("/api/document/analyze", files=files, headers=headers)
    assert resp.status_code == 400
