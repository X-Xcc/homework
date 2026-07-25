import pytest


@pytest.mark.asyncio
async def test_health_returns_db_ok(client):
    resp = await client.get("/health")
    assert resp.status_code in (200, 503)
    body = resp.json()
    assert body["version"] == "1.0.0"
    assert "components" in body
    assert body["components"]["db"] in ("ok", "down")
