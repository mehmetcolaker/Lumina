"""Health-check endpoint tests."""

from httpx import AsyncClient


class TestHealth:
    async def test_health(self, async_client: AsyncClient):
        resp = await async_client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
