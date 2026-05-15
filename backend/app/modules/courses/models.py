import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum as SAEnum, JSON, Uuid
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.progress.models import UserProgress


class StepType(str, enum.Enum):
    THEORY = "theory"
    QUIZ = "quiz"
    CODE = "code"


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    runtime_language: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    runtime_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    outcomes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    prerequisites: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    sections: Mapped[List["Section"]] = relationship(
        back_populates="course", lazy="selectin", order_by="Section.order", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Course id={self.id} title={self.title}>"


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    course: Mapped["Course"] = relationship(back_populates="sections", lazy="selectin")
    steps: Mapped[List["Step"]] = relationship(
        back_populates="section", lazy="selectin", order_by="Step.order", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Section id={self.id} title={self.title} order={self.order}>"


class Step(Base):
    __tablename__ = "steps"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    section_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    step_type: Mapped[StepType] = mapped_column(SAEnum(StepType, name="step_type_enum", create_constraint=True), nullable=False)
    content_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    runtime_language: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    runtime_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    previewable: Mapped[bool] = mapped_column(default=False, nullable=False)

    section: Mapped["Section"] = relationship(back_populates="steps", lazy="selectin")

    if TYPE_CHECKING:
        user_progresses: Mapped[List["UserProgress"]] = relationship(
            back_populates="step", lazy="selectin", cascade="all, delete-orphan",
        )

    def __repr__(self) -> str:
        return f"<Step id={self.id} title={self.title} type={self.step_type} order={self.order}>"


# ── Learning Path (Roadmap) ─────────────────────────────

class LearningPath(Base):
    """A curated learning path/roadmap (e.g. "Python Developer Roadmap")."""

    __tablename__ = "learning_paths"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    icon: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)

    levels: Mapped[List["PathLevel"]] = relationship(
        back_populates="path", lazy="selectin", order_by="PathLevel.order", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<LearningPath id={self.id} title={self.title}>"


class PathLevel(Base):
    """A single level/stop within a LearningPath, linked to a Course.

    Attributes:
        path_id: Foreign key to LearningPath.
        course_id: Foreign key to Course.
        level_name: Display name like "Beginner 1", "Intermediate 2".
        order: Ordinal position within the path (1-based).
        required_progress_pct: % of previous level steps that must be
                               completed before this level unlocks.
    """

    __tablename__ = "path_levels"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    path_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    level_name: Mapped[str] = mapped_column(String(100), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    required_progress_pct: Mapped[int] = mapped_column(Integer, nullable=False, default=75)

    path: Mapped["LearningPath"] = relationship(back_populates="levels", lazy="selectin")
    course: Mapped["Course"] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return f"<PathLevel {self.level_name} order={self.order}>"
