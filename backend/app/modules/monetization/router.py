import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session as SyncSession

from app.core.database import get_sync_db
from app.modules.monetization import services as monetization_services
from app.modules.monetization.schemas import CheckoutResponse, WebhookResponse
from app.modules.users.router import get_current_user
from app.modules.users.schemas import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/monetization", tags=["Monetization"])


@router.post(
    "/checkout",
    response_model=CheckoutResponse,
    summary="Create a Stripe Checkout Session for premium upgrade",
)
async def create_checkout(
    current_user: UserResponse = Depends(get_current_user),
) -> CheckoutResponse:
    """Generate a Stripe-hosted checkout page for a premium subscription.

    The user is redirected to the returned URL to complete payment.
    Requires the user to be authenticated.
    """
    try:
        result = monetization_services.create_checkout_session(
            user_id=current_user.id,
            email=current_user.email,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    return CheckoutResponse(
        checkout_url=result["checkout_url"],
        session_id=result["session_id"],
    )


@router.post(
    "/webhook",
    response_model=WebhookResponse,
    summary="Handle incoming Stripe webhook events",
)
async def stripe_webhook(
    request: Request,
    db: SyncSession = Depends(get_sync_db),
) -> WebhookResponse:
    """Receive and process Stripe webhook events.

    This endpoint is called directly by Stripe.  It reads the raw request
    body to verify the ``Stripe-Signature`` header.

    Important: This endpoint does **not** require authentication.
    """
    sig_header = request.headers.get("stripe-signature")
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header.",
        )

    payload = await request.body()

    try:
        msg = monetization_services.handle_stripe_webhook(
            payload=payload,
            sig_header=sig_header,
            db_session=db,
        )
        logger.info("Webhook processed: %s", msg)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return WebhookResponse(received=True)
