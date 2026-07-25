import pytest

from tests.conftest import auth_header


@pytest.mark.asyncio
async def test_admin_list_users_requires_admin(client, normal_user):
    resp = await client.get("/api/admin/users", headers=auth_header(normal_user))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_stats(client, admin_user, normal_user):
    resp = await client.get("/api/admin/stats", headers=auth_header(admin_user))
    assert resp.status_code == 200
    body = resp.json()
    assert body["user_total"] >= 2  # admin + normal_user
    assert body["user_admin"] >= 1
    assert "analysis_total" in body


@pytest.mark.asyncio
async def test_admin_list_users_pagination(client, admin_user, normal_user):
    resp = await client.get(
        "/api/admin/users?page=1&page_size=10",
        headers=auth_header(admin_user),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["page"] == 1
    assert body["page_size"] == 10
    assert body["total"] >= 1
    usernames = {u["username"] for u in body["items"]}
    assert "alice" in usernames


@pytest.mark.asyncio
async def test_admin_update_user_nickname(client, admin_user, normal_user):
    resp = await client.patch(
        f"/api/admin/users/{normal_user.id}",
        headers=auth_header(admin_user),
        json={"nickname": "AliceUpdated"},
    )
    assert resp.status_code == 200
    assert resp.json()["nickname"] == "AliceUpdated"


@pytest.mark.asyncio
async def test_admin_cannot_demote_last_admin(client, admin_user):
    """admin_user 自身是唯一管理员，尝试降级应被拒。"""
    resp = await client.patch(
        f"/api/admin/users/{admin_user.id}",
        headers=auth_header(admin_user),
        json={"role": "user"},
    )
    assert resp.status_code == 400
