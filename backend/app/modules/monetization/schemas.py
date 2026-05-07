from pydantic import BaseModel, Field


class CheckoutResponse(BaseModel):
    """URL returned after creating a Stripe Checkout Session.

    Attributes:
        checkout_url: The Stripe-hosted checkout page URL.
        session_id: The Stripe Checkout Session ID (for idempotency).
    """

    checkout_url: str
    session_id: str


class WebhookResponse(BaseModel):
    """Response returned to Stripe after processing a webhook event.

    Attributes:
        received: Always ``True`` when the response is successful.
    """

    received: bool = True
