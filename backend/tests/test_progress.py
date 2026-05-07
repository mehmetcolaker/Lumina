"""Tests for the Progress module."""

import pytest
from httpx import AsyncClient


class TestCompleteStep:
    async def test_complete_success(
        self, async_client: AsyncClient, seeded_course, auth_headers
    ):
        step_id = seeded_course.sections[0].steps[0].id
        resp = await async_client.post(
            f"/api/v1/progress/steps/{step_id}/complete",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["step_id"] == str(step_id)
        assert data["xp_earned"] == 10

    async def test_complete_duplicate(
        self, async_client: AsyncClient, seeded_course, auth_headers
    ):
        step_id = seeded_course.sections[0].steps[0].id
        # First completion
        await async_client.post(
            f"/api/v1/progress/steps/{step_id}/complete",
            headers=auth_headers,
        )
        # Second attempt should fail
        resp = await async_client.post(
            f"/api/v1/progress/steps/{step_id}/complete",
            headers=auth_headers,
        )
        assert resp.status_code == 400

    async def test_complete_unauthorized(
        self, async_client: AsyncClient, seeded_course
    ):
        step_id = seeded_course.sections[0].steps[0].id
        resp = await async_client.post(
            f"/api/v1/progress/steps/{step_id}/complete",
        )
        assert resp.status_code in (401, 403)

    async def test_complete_nonexistent_step(
        self, async_client: AsyncClient, auth_headers
    ):
        resp = await async_client.post(
            "/api/v1/progress/steps/00000000-0000-0000-0000-000000000000/complete",
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestMyPath:
    async def test_my_path(
        self, async_client: AsyncClient, seeded_course, auth_headers
    ):
        # Complete first step
        step_id = seeded_course.sections[0].steps[0].id
        await async_client.post(
            f"/api/v1/progress/steps/{step_id}/complete",
            headers=auth_headers,
        )

        # Get my path
        resp = await async_client.get(
            f"/api/v1/progress/my-path/{seeded_course.id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["course_id"] == str(seeded_course.id)
        section = data["sections"][0]
        assert section["steps"][0]["is_completed"] is True
        assert section["steps"][1]["is_completed"] is False

    async def test_my_path_not_found(
        self, async_client: AsyncClient, auth_headers
    ):
        resp = await async_client.get(
            "/api/v1/progress/my-path/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    async def test_my_path_unauthorized(
        self, async_client: AsyncClient, seeded_course
    ):
        resp = await async_client.get(
            f"/api/v1/progress/my-path/{seeded_course.id}",
        )
        assert resp.status_code in (401, 403)
