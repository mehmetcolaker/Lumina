import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, Text, Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SubmissionStatus(str, enum.Enum):
    """Possible states of a code submission lifecycle."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SubmissionVerdict(str, enum.Enum):
    """Evaluation result of a graded submission."""

    PASS = "pass"
    FAIL = "fail"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
    WRONG_ANSWER = "wrong_answer"
    PENDING = "pending"


class Submission(Base):
    """Records a single code submission from a user.

    Attributes:
        id: Primary key (UUID v4).
        user_id: Foreign key to the submitting User.
        step_id: Foreign key to the Step the code belongs to.
        code: The raw source code submitted by the user.
        status: Current execution status.
        output: Legacy combined stdout+stderr.
        stdout: Standart cikti.
        stderr: Hata ciktisi.
        exit_code: Cikis kodu (0 = basarili).
        runtime_ms: Calisma suresi milisaniye.
        verdict: Degerlendirme sonucu.
        test_results: JSON array of per-test-case results.
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
    stdout: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    stderr: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    runtime_ms: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    verdict: Mapped[SubmissionVerdict | None] = mapped_column(
        SAEnum(
            SubmissionVerdict,
            name="submission_verdict_enum",
            create_constraint=True,
        ),
        nullable=True,
        default=None,
    )
    test_results: Mapped[list[dict] | None] = mapped_column(
        JSON,
        nullable=True,
        default=None,
    )
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
