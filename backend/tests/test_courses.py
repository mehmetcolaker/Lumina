"""Tests for the Courses module."""

from httpx import AsyncClient


class TestListCourses:
    ENDPOINT = "/api/v1/courses/"

    async def test_list_empty(self, async_client: AsyncClient):
        resp = await async_client.get(self.ENDPOINT)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_with_data(self, async_client: AsyncClient, seeded_course_data):
        resp = await async_client.get(self.ENDPOINT)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Course"
        assert data[0]["language"] == "Python"


class TestCoursePath:
    async def test_path_success(self, async_client: AsyncClient, seeded_course_data):
        resp = await async_client.get(
            f"/api/v1/courses/{seeded_course_data['course_id']}/path"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == seeded_course_data["course_id"]
        assert len(data["sections"]) == 1
        section = data["sections"][0]
        assert section["title"] == "Section 1"
        assert len(section["steps"]) == 2
        assert section["steps"][0]["step_type"] == "theory"
        assert section["steps"][1]["step_type"] == "quiz"

    async def test_path_not_found(self, async_client: AsyncClient):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await async_client.get(f"/api/v1/courses/{fake_id}/path")
        assert resp.status_code == 404

    async def test_path_invalid_uuid(self, async_client: AsyncClient):
        resp = await async_client.get("/api/v1/courses/not-a-uuid/path")
        assert resp.status_code == 422
