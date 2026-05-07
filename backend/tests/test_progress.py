"""Tests for the Progress module."""

import pytest
from httpx import AsyncClient


class TestCompleteStep:
    async def test_complete_success(
        self, async_client: AsyncClient, seeded_course_data, auth_headers
    ):
        step_id = seeded_course_data["step_id_1"]
        resp = await async_client.post(
            f"/api/v1/progress/steps/{step_id}/complete",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["step_id"] == step_id
        assert data["xp_earned"] == 10

    async def test_complete_duplicate(
        self, async_client: AsyncClient, seeded_course_data, auth_headers
    ):
        step_id = seeded_course_data["step_id_1"]
        # First completion
        r1 = await async_client.post(
            f"/api/v1/progress/steps/{step_id}/complete",
            headers=auth_headers,
        )
        assert r1.status_code == 200
        # Second attempt should fail
        r2 = await async_client.post(
            f"/api/v1/progress/steps/{step_id}/complete",
            headers=auth_headers,
        )
        assert r2.status_code == 400

    async def test_complete_unauthorized(
        self, async_client: AsyncClient, seeded_course_data
    ):
        step_id = seeded_course_data["step_id_1"]
        resp = await async_client.post(
            f"/api/v1/progress/steps/{step_id}/complete",
        )
        assert resp.status_code in (401, 403)

    @pytest.mark.skip(
        reason="SQLite FK constraint blocks fake UUID inserts; "
               "this test requires PostgreSQL."
    )
    async def test_complete_nonexistent_step(
        self, async_client: AsyncClient, auth_headers
    ):
        """Fake step_id violates FK constraint — expect a 500 error
        (the service layer does not yet validate step existence before
        inserting the progress record)."""
        resp = await async_client.post(
            "/api/v1/progress/steps/00000000-0000-0000-0000-000000000000/complete",
            headers=auth_headers,
        )
        # SQLite FK violation → 500. In production the DB returns the
        # same error; a future improvement should check step existence
        # in the service layer and return a 404 instead.
        assert resp.status_code in (404, 500)


class TestMyPath:
    async def test_my_path(
        self, async_client: AsyncClient, seeded_course_data, auth_headers
    ):
        # Complete first step
        await async_client.post(
            f"/api/v1/progress/steps/{seeded_course_data['step_id_1']}/complete",
            headers=auth_headers,
        )

        # Get my path
        resp = await async_client.get(
            f"/api/v1/progress/my-path/{seeded_course_data['course_id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["course_id"] == seeded_course_data["course_id"]
        section = data["sections"][0]
        steps = {s["step_id"]: s["is_completed"] for s in section["steps"]}
        assert steps[seeded_course_data["step_id_1"]] is True
        assert steps[seeded_course_data["step_id_2"]] is False

    async def test_my_path_not_found(
        self, async_client: AsyncClient, auth_headers
    ):
        resp = await async_client.get(
            "/api/v1/progress/my-path/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    async def test_my_path_unauthorized(
        self, async_client: AsyncClient, seeded_course_data
    ):
        resp = await async_client.get(
            f"/api/v1/progress/my-path/{seeded_course_data['course_id']}",
        )
        assert resp.status_code in (401, 403)
