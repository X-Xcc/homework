import pytest

from app.core.security import create_access_token


@pytest.fixture
def _patched_ai(monkeypatch):
    """把 ai_analyzer 的 chat 替换成常量返回，避免真实调用 MiMo。"""
    import sys

    mod = sys.modules["app.core.ai_analyzer"]

    async def fake_chat(message, history=None, context=None):
        return f"echo: {message}"

    async def fake_chat_stream(message, history=None, context=None):
        for chunk in ["hi", " ", "there"]:
            yield chunk

    monkeypatch.setattr(mod.ai_analyzer, "chat", fake_chat)
    monkeypatch.setattr(mod.ai_analyzer, "chat_stream", fake_chat_stream)


def _auth_headers(user):
    token = create_access_token(user.id, user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_and_send_message(client, normal_user, _patched_ai):
    headers = _auth_headers(normal_user)

    # 创建会话
    resp = await client.post(
        "/api/chat/sessions",
        json={"title": "test session"},
        headers=headers,
    )
    assert resp.status_code == 200
    session = resp.json()
    assert "id" in session

    # 发消息
    resp = await client.post(
        f"/api/chat/sessions/{session['id']}/messages",
        json={"role": "user", "content": "hi"},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "assistant"
    assert "hi" in body["content"]


@pytest.mark.asyncio
async def test_list_sessions_empty(client, normal_user):
    headers = _auth_headers(normal_user)
    resp = await client.get("/api/chat/sessions", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_delete_session(client, normal_user, _patched_ai):
    headers = _auth_headers(normal_user)

    # 创建
    resp = await client.post("/api/chat/sessions", json={"title": "x"}, headers=headers)
    assert resp.status_code == 200
    session_id = resp.json()["id"]

    # 删除
    resp = await client.delete(f"/api/chat/sessions/{session_id}", headers=headers)
    assert resp.status_code == 200
