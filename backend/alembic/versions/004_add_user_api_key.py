"""Add user api_key for Agent 认证

Revision ID: 004
Revises: 003
Create Date: 2025-02-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 幂等：若列已存在则跳过，避免重复迁移报错
    conn = op.get_bind()
    r = conn.execute(text(
        "SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='api_key'"
    ))
    if r.scalar() is None:
        op.add_column("users", sa.Column("api_key", sa.String(64), nullable=True))
        op.create_index("ix_users_api_key", "users", ["api_key"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_api_key", table_name="users")
    op.drop_column("users", "api_key")
