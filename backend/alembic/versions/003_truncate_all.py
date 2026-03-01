"""清空所有数据记录（含用户）

Revision ID: 003
Revises: 002
Create Date: 2025-02-28

"""
import os
from typing import Sequence, Union

from alembic import op


revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    allow_destructive = os.getenv("ALLOW_DESTRUCTIVE_MIGRATIONS", "false").lower() in {"1", "true", "yes"}
    if not allow_destructive:
        # 默认跳过破坏性迁移，避免新环境初始化时误删历史数据
        return
    # 按外键依赖顺序清空：子表先于父表
    op.execute(
        "TRUNCATE TABLE activities, documents, knowledge_base_members, knowledge_bases, users "
        "RESTART IDENTITY CASCADE"
    )


def downgrade() -> None:
    pass  # 无法恢复已删除的数据
