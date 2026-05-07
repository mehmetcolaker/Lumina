import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserStats(Base):
    """Aggregated gamification stats for a single user.

    Each user has exactly one UserStats row (created on first XP award).
    The ``total_xp`` column is the source of truth; Redis leaderboard
    values are kept in sync via ``services.award_xp``.

    Attributes:
        id: Primary key (UUID v4).
        user_id: Foreign key to the User (unique → one-to-one).
        total_xp: Cumulative experience points.
        current_streak: Consecutive daily-active count.
        last_active_date: The most recent date the user was active.
    """

    __tablename__ = "user_stats"

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
    total_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<UserStats user_id={self.user_id} total_xp={self.total_xp}>"
        )


class LineComment(Base):
    """A comment attached to a specific line of code within a step.

    Enables the "line-by-line commentary" feature where learners can
    ask questions or leave notes on individual lines of code examples.

    Attributes:
        id: Primary key (UUID v4).
        step_id: Foreign key to the Step being commented on.
        user_id: Foreign key to the comment author.
        line_number: The 1-based line number the comment refers to.
        content: The comment body.
        created_at: Timestamp of creation.
    """

    __tablename__ = "line_comments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    step_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("steps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<LineComment id={self.id} step_id={self.step_id} "
            f"line={self.line_number}>"
        )
