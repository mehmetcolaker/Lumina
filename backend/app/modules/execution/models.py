import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SubmissionStatus(str, enum.Enum):
    """Possible states of a code submission lifecycle."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Submission(Base):
    """Records a single code submission from a user.

    Each submission captures the code snapshot, its execution status,
    and the final output or error message produced by the sandbox.

    Attributes:
        id: Primary key (UUID v4).
        user_id: Foreign key to the submitting User.
        step_id: Foreign key to the Step the code belongs to.
        code: The raw source code submitted by the user.
        status: Current execution status (pending/running/completed/failed).
        output: Combined stdout + stderr from the sandbox run.
        created_at: Timestamp of submission creation.
    """

    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("steps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        SAEnum(
            SubmissionStatus,
            name="submission_status_enum",
            create_constraint=True,
        ),
        default=SubmissionStatus.PENDING,
        nullable=False,
        index=True,
    )
    output: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Submission id={self.id} user_id={self.user_id} "
            f"status={self.status.value}>"
        )
