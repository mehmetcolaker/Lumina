"""Tests for the Authentication & Users module."""

import pytest
from httpx import AsyncClient


class TestRegister:
    ENDPOINT = "/api/v1/auth/register"

    async def test_register_success(self, async_client: AsyncClient):
        payload = {"email": "newuser@test.dev", "password": "strongpass123"}
        resp = await async_client.post(self.ENDPOINT, json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "newuser@test.dev"
        assert data["is_active"] is True
        assert data["is_premium"] is False
        assert "id" in data

    async def test_register_duplicate_email(self, async_client: AsyncClient, demo_user):
        payload = {"email": "demo@test.dev", "password": "anotherpass123"}
        resp = await async_client.post(self.ENDPOINT, json=payload)
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]

    async def test_register_weak_password(self, async_client: AsyncClient):
        payload = {"email": "weak@test.dev", "password": "short"}
        resp = await async_client.post(self.ENDPOINT, json=payload)
        assert resp.status_code == 422

    async def test_register_invalid_email(self, async_client: AsyncClient):
        payload = {"email": "not-an-email", "password": "strongpass123"}
        resp = await async_client.post(self.ENDPOINT, json=payload)
        assert resp.status_code == 422


class TestLogin:
    ENDPOINT = "/api/v1/auth/login"

    async def test_login_success(self, async_client: AsyncClient, demo_user):
        resp = await async_client.post(
            self.ENDPOINT,
            data={"username": "demo@test.dev", "password": "demopass123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"

    async def test_login_wrong_password(self, async_client: AsyncClient, demo_user):
        resp = await async_client.post(
            self.ENDPOINT,
            data={"username": "demo@test.dev", "password": "wrongpass"},
        )
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        resp = await async_client.post(
            self.ENDPOINT,
            data={"username": "nobody@test.dev", "password": "somepass"},
        )
        assert resp.status_code == 401


class TestUsersMe:
    ENDPOINT = "/api/v1/users/me"

    async def test_me_authenticated(self, async_client: AsyncClient, auth_headers):
        resp = await async_client.get(self.ENDPOINT, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "demo@test.dev"

    async def test_me_unauthenticated(self, async_client: AsyncClient):
        resp = await async_client.get(self.ENDPOINT)
        # OAuth2PasswordBearer returns 401 (not 403) when no token is sent
        assert resp.status_code in (401, 403)

    async def test_me_invalid_token(self, async_client: AsyncClient):
        headers = {"Authorization": "Bearer invalidtoken"}
        resp = await async_client.get(self.ENDPOINT, headers=headers)
        assert resp.status_code == 401
