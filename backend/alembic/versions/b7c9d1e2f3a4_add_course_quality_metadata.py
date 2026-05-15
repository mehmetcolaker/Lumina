"""add course quality metadata

Revision ID: b7c9d1e2f3a4
Revises: a1b2c3d4e5f6
Create Date: 2026-05-13 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c9d1e2f3a4"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("courses", sa.Column("level", sa.String(length=50), nullable=True))
    op.add_column("courses", sa.Column("runtime_language", sa.String(length=50), nullable=True))
    op.add_column("courses", sa.Column("runtime_version", sa.String(length=50), nullable=True))
    op.add_column("courses", sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("courses", sa.Column("outcomes", sa.JSON(), nullable=True))
    op.add_column("courses", sa.Column("prerequisites", sa.JSON(), nullable=True))
    op.add_column("steps", sa.Column("runtime_language", sa.String(length=50), nullable=True))
    op.add_column("steps", sa.Column("runtime_version", sa.String(length=50), nullable=True))
    op.add_column("steps", sa.Column("previewable", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column("steps", "previewable", server_default=None)


def downgrade() -> None:
    op.drop_column("steps", "previewable")
    op.drop_column("steps", "runtime_version")
    op.drop_column("steps", "runtime_language")
    op.drop_column("courses", "prerequisites")
    op.drop_column("courses", "outcomes")
    op.drop_column("courses", "last_reviewed_at")
    op.drop_column("courses", "runtime_version")
    op.drop_column("courses", "runtime_language")
    op.drop_column("courses", "level")
