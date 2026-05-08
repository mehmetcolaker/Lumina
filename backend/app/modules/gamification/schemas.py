from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ---------- Leaderboard ----------


class LeaderboardEntry(BaseModel):
    """A single entry in the global leaderboard.

    Attributes:
        rank: Ordinal position (1-based).
        user_id: The user's UUID.
        email: The user's email address (for display).
        total_xp: The user's cumulative XP.
    """

    rank: int
    user_id: UUID
    email: str
    total_xp: int


class LeaderboardResponse(BaseModel):
    """Top-N users sorted by XP descending.

    Attributes:
        entries: Ordered list of leaderboard entries.
    """

    entries: list[LeaderboardEntry]


# ---------- Line comments ----------


class CommentCreate(BaseModel):
    """Request body to attach a comment to a specific code line.

    Attributes:
        step_id: UUID of the step being commented on.
        line_number: 1-based line number within the step content.
        content: The comment text.
    """

    step_id: UUID
    line_number: int = Field(..., ge=1, description="1-based line number")
    content: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    """A single line comment with author info.

    Attributes:
        id: Comment UUID.
        step_id: Parent step UUID.
        user_id: Author UUID.
        email: Author's email.
        line_number: The line this comment refers to.
        content: Comment body.
        created_at: Creation timestamp.
    """

    id: UUID
    step_id: UUID
    user_id: UUID
    email: str = ""
    line_number: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Badges ----------


class BadgeResponse(BaseModel):
    """A single badge owned by a user or a badge definition."""

    badge_type: str
    title: str
    emoji: str
    description: str | None = None
    earned_at: datetime | None = None
    owned: bool = False


class UserBadgesResponse(BaseModel):
    """All badges for a user categorized by owned/unlocked status."""

    owned: list[BadgeResponse]
    locked: list[BadgeResponse]
