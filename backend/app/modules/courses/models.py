import enum
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Enum as SAEnum, JSON, Uuid
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.progress.models import UserProgress


class StepType(str, enum.Enum):
    """Enumeration of possible step content types.

    Attributes:
        THEORY: Theoretical / explanatory content.
        QUIZ: Multiple-choice or fill-in assessment.
        CODE: Interactive coding exercise.
    """

    THEORY = "theory"
    QUIZ = "quiz"
    CODE = "code"


class Course(Base):
    """A top-level course entity (e.g. "Python Fundamentals").

    Attributes:
        id: Primary key (UUID v4).
        title: Human-readable course title.
        description: Longer course description / teaser.
        language: Programming language this course targets (e.g. "Python").
        sections: Ordered list of Section records belonging to this course.
    """

    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    sections: Mapped[List["Section"]] = relationship(
        back_populates="course",
        lazy="selectin",
        order_by="Section.order",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Course id={self.id} title={self.title}>"


class Section(Base):
    """A chapter / section within a Course.

    Attributes:
        id: Primary key (UUID v4).
        course_id: Foreign key to the parent Course.
        title: Section title (e.g. "Variables & Data Types").
        order: Ordinal position within the course (0-based).
        course: The parent Course ORM relationship.
        steps: Ordered list of Step records within this section.
    """

    __tablename__ = "sections"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    course: Mapped["Course"] = relationship(
        back_populates="sections",
        lazy="selectin",
    )
    steps: Mapped[List["Step"]] = relationship(
        back_populates="section",
        lazy="selectin",
        order_by="Step.order",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Section id={self.id} title={self.title} order={self.order}>"


class Step(Base):
    """An atomic learning unit within a Section.

    Attributes:
        id: Primary key (UUID v4).
        section_id: Foreign key to the parent Section.
        title: Step title (e.g. "What is a Variable?").
        step_type: Content type — theory, quiz, or code.
        content_data: Flexible JSON payload storing step-specific data
                      (markdown body, quiz options, code template, etc.).
        order: Ordinal position within the section (0-based).
        xp_reward: Experience points awarded upon completion.
        section: The parent Section ORM relationship.
        user_progresses: UserProgress records for this step.
    """

    __tablename__ = "steps"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    section_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("sections.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    step_type: Mapped[StepType] = mapped_column(
        SAEnum(StepType, name="step_type_enum", create_constraint=True),
        nullable=False,
    )
    content_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    section: Mapped["Section"] = relationship(
        back_populates="steps",
        lazy="selectin",
    )

    if TYPE_CHECKING:
        user_progresses: Mapped[List["UserProgress"]] = relationship(
            back_populates="step",
            lazy="selectin",
            cascade="all, delete-orphan",
        )

    def __repr__(self) -> str:
        return (
            f"<Step id={self.id} title={self.title} "
            f"type={self.step_type} order={self.order}>"
        )
