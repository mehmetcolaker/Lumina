"""Tests for the Monetization (Stripe) module.

These tests verify the checkout endpoint authorisation and the webhook
endpoint signature validation.  Actual Stripe API calls are mocked.
"""

from unittest.mock import patch

import pytest
from httpx import AsyncClient


class TestCheckout:
    ENDPOINT = "/api/v1/monetization/checkout"

    async def test_checkout_requires_auth(self, async_client: AsyncClient):
        resp = await async_client.post(self.ENDPOINT)
        # OAuth2PasswordBearer returns 401 when no token is sent
        assert resp.status_code in (401, 403)

    @patch("app.modules.monetization.services.settings.STRIPE_SECRET_KEY", "sk_test_123")
    @patch("app.modules.monetization.services.settings.STRIPE_PRICE_ID", "price_test")
    @patch("app.modules.monetization.services.stripe.checkout.Session.create")
    async def test_checkout_success(
        self, mock_create, async_client: AsyncClient, auth_headers
    ):
        mock_create.return_value.url = "https://checkout.stripe.com/test"
        mock_create.return_value.id = "cs_test_123"

        resp = await async_client.post(self.ENDPOINT, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "checkout_url" in data
        assert "session_id" in data
        assert data["session_id"] == "cs_test_123"


class TestWebhook:
    ENDPOINT = "/api/v1/monetization/webhook"

    async def test_webhook_missing_signature(self, async_client: AsyncClient):
        resp = await async_client.post(
            self.ENDPOINT,
            content=b"{}",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        assert "stripe-signature" in resp.json()["detail"].lower()

    @patch("app.modules.monetization.services.settings.STRIPE_WEBHOOK_SECRET", "whsec_test")
    async def test_webhook_invalid_signature(self, async_client: AsyncClient):
        resp = await async_client.post(
            self.ENDPOINT,
            content=b"{}",
            headers={
                "Content-Type": "application/json",
                "stripe-signature": "bad_sig",
            },
        )
        assert resp.status_code == 400

    @patch("app.modules.monetization.services.settings.STRIPE_WEBHOOK_SECRET", "whsec_test")
    @patch("app.modules.monetization.services.stripe.Webhook.construct_event")
    async def test_webhook_success(
        self, mock_construct, async_client: AsyncClient
    ):
        mock_construct.return_value = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_test",
                    "status": "active",
                    "current_period_end": 9999999999,
                }
            },
        }

        resp = await async_client.post(
            self.ENDPOINT,
            content=b'{"test": true}',
            headers={
                "Content-Type": "application/json",
                "stripe-signature": "valid_sig",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["received"] is True
