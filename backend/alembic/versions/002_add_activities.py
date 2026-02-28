"""Add activities table

Revision ID: 002
Revises: 001
Create Date: 2025-02-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "activities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.Enum("create_kb", "upload_doc", "add_member", "create_note", name="activityaction"), nullable=False),
        sa.Column("knowledge_base_id", sa.Integer(), nullable=True),
        sa.Column("extra", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["knowledge_base_id"], ["knowledge_bases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activities_id", "activities", ["id"])
    op.create_index("ix_activities_created_at", "activities", ["created_at"])


def downgrade() -> None:
    op.drop_table("activities")
    op.execute("DROP TYPE IF EXISTS activityaction")
