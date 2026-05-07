"""Tests for the Gamification module."""

from httpx import AsyncClient


class TestLeaderboard:
    ENDPOINT = "/api/v1/gamification/leaderboard"

    async def test_leaderboard_empty(self, async_client: AsyncClient):
        resp = await async_client.get(self.ENDPOINT)
        assert resp.status_code == 200
        assert resp.json()["entries"] == []

    async def test_leaderboard_with_stats(
        self, async_client: AsyncClient, seeded_course_data, auth_headers
    ):
        # Complete a step to earn XP (triggers award_xp)
        await async_client.post(
            f"/api/v1/progress/steps/{seeded_course_data['step_id_1']}/complete",
            headers=auth_headers,
        )

        resp = await async_client.get(self.ENDPOINT)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["entries"]) == 1
        entry = data["entries"][0]
        assert entry["total_xp"] >= 10
        assert entry["rank"] == 1

    async def test_leaderboard_limit(self, async_client: AsyncClient):
        resp = await async_client.get(f"{self.ENDPOINT}?limit=0")
        assert resp.status_code == 422
        resp = await async_client.get(f"{self.ENDPOINT}?limit=101")
        assert resp.status_code == 422


class TestComments:
    async def test_add_comment(
        self, async_client: AsyncClient, seeded_course_data, auth_headers
    ):
        payload = {
            "step_id": seeded_course_data["step_id_1"],
            "line_number": 5,
            "content": "Great explanation!",
        }
        resp = await async_client.post(
            "/api/v1/gamification/comments",
            json=payload,
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["line_number"] == 5
        assert data["content"] == "Great explanation!"

    async def test_add_comment_requires_auth(
        self, async_client: AsyncClient, seeded_course_data
    ):
        payload = {
            "step_id": seeded_course_data["step_id_1"],
            "line_number": 1,
            "content": "Nice!",
        }
        resp = await async_client.post(
            "/api/v1/gamification/comments", json=payload
        )
        assert resp.status_code in (401, 403)

    async def test_get_comments(
        self, async_client: AsyncClient, seeded_course_data, auth_headers
    ):
        for i, text in enumerate(["First!", "Second!"], 1):
            await async_client.post(
                "/api/v1/gamification/comments",
                json={
                    "step_id": seeded_course_data["step_id_1"],
                    "line_number": i,
                    "content": text,
                },
                headers=auth_headers,
            )

        resp = await async_client.get(
            f"/api/v1/gamification/comments/{seeded_course_data['step_id_1']}",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["content"] == "First!"
        assert data[1]["content"] == "Second!"

    async def test_get_comments_empty(
        self, async_client: AsyncClient, seeded_course_data
    ):
        resp = await async_client.get(
            f"/api/v1/gamification/comments/{seeded_course_data['step_id_1']}",
        )
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_get_comments_invalid_step_id(self, async_client: AsyncClient):
        resp = await async_client.get(
            "/api/v1/gamification/comments/not-a-uuid",
        )
        assert resp.status_code == 422
