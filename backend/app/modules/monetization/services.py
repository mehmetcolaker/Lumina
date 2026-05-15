"""Stripe payment and subscription management.

Handles creation of Checkout Sessions and processing of Stripe webhook
events (customer.subscription.created / updated / deleted).
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

import stripe
from sqlalchemy import select
from sqlalchemy.orm import Session as SyncSession  # noqa: N812

from app.core.config import settings
from app.modules.monetization.models import PlanType, Subscription
from app.modules.users.models import User

logger = logging.getLogger(__name__)

# Configure Stripe SDK
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(
    user_id: UUID,
    email: str,
) -> dict:
    """Create a Stripe Checkout Session for a premium subscription.

    Args:
        user_id: The Lumina user UUID.
        email: The user's email address (pre-filled on Stripe's form).

    Returns:
        A dict with keys ``checkout_url`` and ``session_id``.

    Raises:
        RuntimeError: If Stripe API key is not configured.
    """
    if not settings.STRIPE_SECRET_KEY:
        raise RuntimeError("Stripe secret key is not configured.")

    if not settings.STRIPE_PRICE_ID:
        raise RuntimeError("Stripe price ID is not configured.")

    session = stripe.checkout.Session.create(
        customer_email=email,
        client_reference_id=str(user_id),
        payment_method_types=["card"],
        mode="subscription",
        line_items=[
            {
                "price": settings.STRIPE_PRICE_ID,
                "quantity": 1,
            }
        ],
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
        metadata={
            "user_id": str(user_id),
        },
    )

    return {
        "checkout_url": session.url,
        "session_id": session.id,
    }


def handle_stripe_webhook(
    payload: bytes,
    sig_header: str,
    db_session: SyncSession,
) -> str:
    """Process an incoming Stripe webhook event.

    Verifies the signature, then handles the following event types:

        - ``checkout.session.completed``
        - ``customer.subscription.updated``
        - ``customer.subscription.deleted``

    Args:
        payload: The raw request body bytes.
        sig_header: The ``Stripe-Signature`` header value.
        db_session: A synchronous SQLAlchemy session.

    Returns:
        A description string summarising what was handled.

    Raises:
        ValueError: If signature verification fails.
    """
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise RuntimeError("Stripe webhook secret is not configured.")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError as exc:
        raise ValueError("Invalid Stripe webhook signature.") from exc

    event_type = event["type"]
    event_data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(event_data, db_session)
        return "checkout.session.completed handled."

    if event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
        _handle_subscription_event(event_data, db_session)
        return f"{event_type} handled."

    logger.info("Unhandled Stripe webhook event type: %s", event_type)
    return f"Event type '{event_type}' ignored."


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------


def _handle_checkout_completed(data: dict, db: SyncSession) -> None:
    """Activate a subscription after a successful checkout."""
    user_id = data.get("metadata", {}).get("user_id")
    if not user_id:
        logger.warning("checkout.session.completed missing user_id in metadata.")
        return

    customer_id = data.get("customer")
    subscription_id = data.get("subscription")

    # Fetch or create the Subscription record
    stmt = select(Subscription).where(Subscription.user_id == UUID(user_id))
    sub = db.execute(stmt).scalar_one_or_none()

    if sub is None:
        sub = Subscription(
            user_id=UUID(user_id),
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            plan_type=PlanType.PREMIUM,
            is_active=True,
        )
        db.add(sub)
    else:
        sub.stripe_customer_id = customer_id
        sub.stripe_subscription_id = subscription_id
        sub.plan_type = PlanType.PREMIUM
        sub.is_active = True

    user = db.get(User, UUID(user_id))
    if user is not None:
        user.is_premium = True

    db.commit()
    logger.info("Subscription activated for user %s", user_id)


def _handle_subscription_event(data: dict, db: SyncSession) -> None:
    """Update or deactivate a subscription based on Stripe events."""
    subscription_id = data.get("id")
    if not subscription_id:
        return

    stmt = select(Subscription).where(
        Subscription.stripe_subscription_id == subscription_id
    )
    sub = db.execute(stmt).scalar_one_or_none()

    if sub is None:
        logger.warning(
            "No local subscription for Stripe ID %s", subscription_id
        )
        return

    status = data.get("status")
    current_period_end = data.get("current_period_end")

    if status == "active":
        sub.is_active = True
        sub.plan_type = PlanType.PREMIUM
        is_premium = True
    elif status in ("canceled", "incomplete_expired", "past_due"):
        sub.is_active = False
        sub.plan_type = PlanType.FREE
        is_premium = False
    else:
        is_premium = sub.is_active

    if current_period_end:
        sub.current_period_end = datetime.fromtimestamp(
            current_period_end, tz=timezone.utc
        )

    user = db.get(User, sub.user_id)
    if user is not None:
        user.is_premium = is_premium

    db.commit()
    logger.info(
        "Subscription %s updated: active=%s", subscription_id, sub.is_active
    )
