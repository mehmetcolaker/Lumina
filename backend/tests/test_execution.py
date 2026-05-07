"""Tests for the Execution (Sandbox) module.

Note: These tests verify the HTTP submission/status logic. The actual
Docker sandbox and Celery worker are not exercised in unit tests.
"""

import pytest
from httpx import AsyncClient


class TestSubmitCode:
    ENDPOINT = "/api/v1/execution/submit"

    async def test_submit_success(
        self, async_client: AsyncClient, seeded_course, auth_headers
    ):
        step_id = seeded_course.sections[0].steps[0].id
        payload = {"step_id": str(step_id), "code": "print('hello')"}
        resp = await async_client.post(
            self.ENDPOINT, json=payload, headers=auth_headers
        )
        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "pending"
        assert "submission_id" in data

    async def test_submit_requires_auth(
        self, async_client: AsyncClient, seeded_course
    ):
        step_id = seeded_course.sections[0].steps[0].id
        payload = {"step_id": str(step_id), "code": "print('hello')"}
        resp = await async_client.post(self.ENDPOINT, json=payload)
        assert resp.status_code in (401, 403)

    async def test_submit_empty_code(
        self, async_client: AsyncClient, seeded_course, auth_headers
    ):
        step_id = seeded_course.sections[0].steps[0].id
        payload = {"step_id": str(step_id), "code": ""}
        resp = await async_client.post(
            self.ENDPOINT, json=payload, headers=auth_headers
        )
        assert resp.status_code == 422


class TestSubmissionStatus:
    async def test_status_pending(
        self, async_client: AsyncClient, seeded_course, auth_headers
    ):
        # Create a submission first
        step_id = seeded_course.sections[0].steps[0].id
        submit_resp = await async_client.post(
            "/api/v1/execution/submit",
            json={"step_id": str(step_id), "code": "print('hi')"},
            headers=auth_headers,
        )
        submission_id = submit_resp.json()["submission_id"]

        # Poll status
        resp = await async_client.get(
            f"/api/v1/execution/status/{submission_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["submission_id"] == submission_id
        assert data["status"] in ("pending", "running")

    async def test_status_not_found(self, async_client: AsyncClient, auth_headers):
        resp = await async_client.get(
            "/api/v1/execution/status/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    async def test_status_unauthorized(self, async_client: AsyncClient):
        resp = await async_client.get(
            "/api/v1/execution/status/00000000-0000-0000-0000-000000000000",
        )
        assert resp.status_code in (401, 403)
