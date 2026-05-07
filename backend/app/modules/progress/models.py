import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.courses.models import Step
    from app.modules.users.models import User


class UserProgress(Base):
    """Tracks a user's completion status for a single step.

    One record per (user, step) pair. If the record exists with
    is_completed=True the step is considered finished.

    Attributes:
        id: Primary key (UUID v4).
        user_id: Foreign key to the User who completed the step.
        step_id: Foreign key to the completed Step.
        is_completed: Whether the step is marked as finished.
        completed_at: Timestamp of when the step was completed.
        user: The User ORM relationship.
        step: The Step ORM relationship.
    """

    __tablename__ = "user_progress"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    step_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("steps.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=True,
    )

    user: Mapped["User"] = relationship(lazy="selectin")
    step: Mapped["Step"] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"<UserProgress id={self.id} user_id={self.user_id} "
            f"step_id={self.step_id} completed={self.is_completed}>"
        )
