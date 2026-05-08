import enum
import uuid
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


# ── Badges ──────────────────────────────────────────────

class BadgeType(str, enum.Enum):
    """Achievement badge types."""
    FIRST_XP = "first_xp"
    STREAK_3 = "streak_3"
    STREAK_7 = "streak_7"
    STREAK_30 = "streak_30"
    XP_100 = "xp_100"
    XP_1000 = "xp_1000"
    XP_5000 = "xp_5000"
    COMPLETE_FIRST = "complete_first"
    COMPLETE_COURSE = "complete_course"
    PYTHON_MASTER = "python_master"
    JS_MASTER = "js_master"
    SQL_MASTER = "sql_master"
    CODE_10 = "code_10"
    CODE_50 = "code_50"
    QUIZ_MASTER = "quiz_master"
    TOP_TEN = "top_ten"
    EARLY_ADOPTER = "early_adopter"


BADGE_DEFINITIONS: dict[str, dict] = {
    BadgeType.FIRST_XP.value: {"title": "Ilk XP", "emoji": "star", "desc": "Ilk XP'ni kazandin!"},
    BadgeType.STREAK_3.value: {"title": "3 Gun Serisi", "emoji": "flame", "desc": "3 gun ust uste ogren"},
    BadgeType.STREAK_7.value: {"title": "Haftalik Seri", "emoji": "flame", "desc": "7 gun ust uste ogren"},
    BadgeType.STREAK_30.value: {"title": "Ayin Aslani", "emoji": "crown", "desc": "30 gun ust uste ogren"},
    BadgeType.XP_100.value: {"title": "100 XP", "emoji": "zap", "desc": "100 XP topla"},
    BadgeType.XP_1000.value: {"title": "1000 XP", "emoji": "gem", "desc": "1000 XP topla"},
    BadgeType.XP_5000.value: {"title": "5000 XP", "emoji": "trophy", "desc": "5000 XP topla"},
    BadgeType.COMPLETE_FIRST.value: {"title": "Ilk Adim", "emoji": "target", "desc": "Ilk adimi tamamla"},
    BadgeType.COMPLETE_COURSE.value: {"title": "Kurs Mezunu", "emoji": "graduation-cap", "desc": "Bir kursu tamamen bitir"},
    BadgeType.PYTHON_MASTER.value: {"title": "Python Ustasi", "emoji": "snake", "desc": "10 Python adimi tamamla"},
    BadgeType.JS_MASTER.value: {"title": "JS Ustasi", "emoji": "zap", "desc": "10 JavaScript adimi tamamla"},
    BadgeType.SQL_MASTER.value: {"title": "SQL Ustasi", "emoji": "database", "desc": "10 SQL adimi tamamla"},
    BadgeType.CODE_10.value: {"title": "10 Kod", "emoji": "code", "desc": "10 kod alistirmasi coz"},
    BadgeType.CODE_50.value: {"title": "50 Kod", "emoji": "code", "desc": "50 kod alistirmasi coz"},
    BadgeType.QUIZ_MASTER.value: {"title": "Quiz Ustasi", "emoji": "brain", "desc": "20 quizi dogru cevapla"},
    BadgeType.TOP_TEN.value: {"title": "Ilk 10", "emoji": "trophy", "desc": "Leaderboard'da ilk 10'a gir"},
    BadgeType.EARLY_ADOPTER.value: {"title": "Oncu", "emoji": "rocket", "desc": "Platformun ilk kullanicilarindan ol"},
}


class UserBadge(Base):
    """A badge earned by a user."""

    __tablename__ = "user_badges"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    badge_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    emoji: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<UserBadge {self.badge_type} user={self.user_id}>"


# ── User Stats ──────────────────────────────────────────

class UserStats(Base):
    """Aggregated gamification stats for a single user."""

    __tablename__ = "user_stats"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    total_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:
        return f"<UserStats user_id={self.user_id} total_xp={self.total_xp}>"


# ── Line Comments ───────────────────────────────────────

class LineComment(Base):
    """A comment attached to a specific line of code within a step."""

    __tablename__ = "line_comments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    step_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("steps.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<LineComment id={self.id} step_id={self.step_id} line={self.line_number}>"
