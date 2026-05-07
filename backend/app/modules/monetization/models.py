import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PlanType(str, enum.Enum):
    """Available subscription plan types for the Lumina platform.

    Attributes:
        FREE: Basic access with limited features.
        PREMIUM: Full access including all courses and features.
    """

    FREE = "free"
    PREMIUM = "premium"


class Subscription(Base):
    """Stripe-backed subscription record for a single user.

    Each user may have at most one active subscription.  The record is
    kept up-to-date via Stripe webhook events.

    Attributes:
        id: Primary key (UUID v4).
        user_id: Foreign key to the user (unique — one subscription per user).
        stripe_customer_id: Stripe Customer object ID.
        stripe_subscription_id: Stripe Subscription object ID.
        plan_type: Current plan (free / premium).
        is_active: Whether the subscription is currently active.
        current_period_end: End of the current billing period (UTC).
        created_at: Record creation timestamp.
        updated_at: Record update timestamp.
    """

    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )
    plan_type: Mapped[PlanType] = mapped_column(
        SAEnum(PlanType, name="plan_type_enum", create_constraint=True),
        default=PlanType.FREE,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Subscription id={self.id} user_id={self.user_id} "
            f"plan={self.plan_type.value} active={self.is_active}>"
        )
