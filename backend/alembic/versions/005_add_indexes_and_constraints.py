"""Add performance indexes and member unique constraint

Revision ID: 005
Revises: 004
Create Date: 2026-03-01

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 清理重复成员，保障后续唯一约束可创建
    op.execute(
        """
        DELETE FROM knowledge_base_members a
        USING knowledge_base_members b
        WHERE a.id > b.id
          AND a.knowledge_base_id = b.knowledge_base_id
          AND a.user_id = b.user_id
        """
    )

    conn = op.get_bind()

    has_unique = conn.execute(
        text(
            """
            SELECT 1
            FROM pg_constraint
            WHERE conname = 'uq_kb_member'
            """
        )
    ).scalar()
    if has_unique is None:
        op.create_unique_constraint(
            "uq_kb_member",
            "knowledge_base_members",
            ["knowledge_base_id", "user_id"],
        )

    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_kb_members_kb_user "
        "ON knowledge_base_members (knowledge_base_id, user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_documents_kb_created_at "
        "ON documents (knowledge_base_id, created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_activities_kb_created_at "
        "ON activities (knowledge_base_id, created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_activities_user_created_at "
        "ON activities (user_id, created_at)"
    )


def downgrade() -> None:
    op.drop_index("ix_activities_user_created_at", table_name="activities")
    op.drop_index("ix_activities_kb_created_at", table_name="activities")
    op.drop_index("ix_documents_kb_created_at", table_name="documents")
    op.drop_index("ix_kb_members_kb_user", table_name="knowledge_base_members")
    op.drop_constraint("uq_kb_member", "knowledge_base_members", type_="unique")
