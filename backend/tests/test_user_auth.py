import pytest


@pytest.mark.asyncio
async def test_register_login_me(client, normal_user):
    """normal_user 已经在 conftest 创建；测试登录 + me + 401。"""
    # 登录
    resp = await client.post(
        "/api/user/login",
        json={"account": "alice", "password": "Strong-Pass-1"},
    )
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # 拿 me
    resp = await client.get(
        "/api/user/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 200
    me = resp.json()
    assert me["username"] == "alice"
    assert me["role"] == "user"


@pytest.mark.asyncio
async def test_login_wrong_password_rejected(client, normal_user):
    resp = await client.post(
        "/api/user/login",
        json={"account": "alice", "password": "wrong-password"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_without_token_returns_401(client):
    resp = await client.get("/api/user/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_register_new_user(client):
    resp = await client.post(
        "/api/user/register",
        json={
            "username": "newbie",
            "password": "Complex-Pass-9",
            "email": "newbie@example.com",
            "nickname": "Newbie",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body


@pytest.mark.asyncio
async def test_register_weak_password_rejected(client):
    resp = await client.post(
        "/api/user/register",
        json={"username": "weak", "password": "abc"},
    )
    assert resp.status_code in (400, 422)


@pytest.mark.asyncio
async def test_register_duplicate_username_rejected(client, normal_user):
    resp = await client.post(
        "/api/user/register",
        json={"username": "alice", "password": "Another-Pass-9"},
    )
    assert resp.status_code == 409
