"""Tests for the Execution (Sandbox) module."""

from httpx import AsyncClient


class TestSubmitCode:
    ENDPOINT = "/api/v1/execution/submit"

    async def test_submit_success(
        self, async_client: AsyncClient, seeded_course_data, auth_headers
    ):
        payload = {
            "step_id": seeded_course_data["step_id_1"],
            "code": "print('hello')",
        }
        resp = await async_client.post(
            self.ENDPOINT, json=payload, headers=auth_headers
        )
        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "pending"
        assert "submission_id" in data

    async def test_submit_requires_auth(
        self, async_client: AsyncClient, seeded_course_data
    ):
        payload = {
            "step_id": seeded_course_data["step_id_1"],
            "code": "print('hello')",
        }
        resp = await async_client.post(self.ENDPOINT, json=payload)
        assert resp.status_code in (401, 403)

    async def test_submit_empty_code(
        self, async_client: AsyncClient, seeded_course_data, auth_headers
    ):
        payload = {
            "step_id": seeded_course_data["step_id_1"],
            "code": "",
        }
        resp = await async_client.post(
            self.ENDPOINT, json=payload, headers=auth_headers
        )
        assert resp.status_code == 422


class TestSubmissionStatus:
    async def test_status_pending(
        self, async_client: AsyncClient, seeded_course_data, auth_headers
    ):
        # Create a submission first
        submit_resp = await async_client.post(
            "/api/v1/execution/submit",
            json={
                "step_id": seeded_course_data["step_id_1"],
                "code": "print('hi')",
            },
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
