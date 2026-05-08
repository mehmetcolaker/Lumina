"""add execution grading fields (stdout, stderr, exit_code, runtime_ms, verdict)

Revision ID: a1b2c3d4e5f6
Revises: 8c65f4d90af5
Create Date: 2026-05-07 22:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "8e7a41a8b030"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Yeni SubmissionVerdict enum tipi
    submission_verdict_enum = sa.Enum(
        "pass", "fail", "runtime_error", "timeout",
        "wrong_answer", "pending",
        name="submission_verdict_enum",
        create_constraint=True,
    )
    submission_verdict_enum.create(op.get_bind())

    # Yeni kolonlar
    op.add_column("submissions", sa.Column("stdout", sa.Text(), nullable=True))
    op.add_column("submissions", sa.Column("stderr", sa.Text(), nullable=True))
    op.add_column("submissions", sa.Column("exit_code", sa.Integer(), nullable=True))
    op.add_column("submissions", sa.Column("runtime_ms", sa.Integer(), nullable=True))
    op.add_column(
        "submissions",
        sa.Column(
            "verdict",
            submission_verdict_enum,
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("submissions", "verdict")
    op.drop_column("submissions", "runtime_ms")
    op.drop_column("submissions", "exit_code")
    op.drop_column("submissions", "stderr")
    op.drop_column("submissions", "stdout")

    submission_verdict_enum = sa.Enum(
        "pass", "fail", "runtime_error", "timeout",
        "wrong_answer", "pending",
        name="submission_verdict_enum",
        create_constraint=True,
    )
    submission_verdict_enum.drop(op.get_bind())
