import pytest

from tests.conftest import auth_header


@pytest.mark.asyncio
async def test_workspace_summary_for_new_user(client, normal_user):
    resp = await client.get("/api/user/workspace", headers=auth_header(normal_user))
    assert resp.status_code == 200
    body = resp.json()
    assert body["stats"]["analysis_count"] == 0
    assert body["stats"]["chat_count"] == 0
    assert body["stats"]["comparison_count"] == 0
    assert body["stats"]["favorite_count"] == 0
    assert body["recent_analyses"] == []
    assert body["recent_sessions"] == []
    assert body["recent_comparisons"] == []
    assert body["favorites"] == []


@pytest.mark.asyncio
async def test_history_default_returns_combined_empty(client, normal_user):
    """新用户：chat + analysis + comparison 都没记录，history 应当是空 list。"""
    resp = await client.get("/api/user/history", headers=auth_header(normal_user))
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_history_filtered_by_chat(client, normal_user):
    resp = await client.get("/api/user/history?type=chat", headers=auth_header(normal_user))
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_add_then_list_favorite(client, normal_user):
    # 收藏
    resp = await client.post(
        "/api/user/favorites",
        json={"item_type": "law", "item_id": "art-1", "title": "第一条", "summary": "测试"},
        headers=auth_header(normal_user),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["message"] == "收藏成功"
    favorite_id = body["id"]

    # 列表
    resp = await client.get("/api/user/favorites", headers=auth_header(normal_user))
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["item_type"] == "law"
    assert items[0]["item_id"] == "art-1"

    # 重复收藏应 400
    resp = await client.post(
        "/api/user/favorites",
        json={"item_type": "law", "item_id": "art-1", "title": "dup"},
        headers=auth_header(normal_user),
    )
    assert resp.status_code == 400

    # 删除
    resp = await client.delete(
        f"/api/user/favorites/{favorite_id}",
        headers=auth_header(normal_user),
    )
    assert resp.status_code == 200

    # 列表再次为空
    resp = await client.get("/api/user/favorites", headers=auth_header(normal_user))
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_me_stats(client, normal_user):
    resp = await client.get("/api/user/me/stats", headers=auth_header(normal_user))
    assert resp.status_code == 200
    body = resp.json()
    assert body["analysis_count"] == 0
    assert body["chat_count"] == 0
    assert body["favorite_count"] == 0
    assert body["comparison_count"] == 0
