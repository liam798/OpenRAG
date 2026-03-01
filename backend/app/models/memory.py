"""跨 agent 公共记忆模型"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class MemoryItem(Base):
    """公共记忆条目"""

    __tablename__ = "memory_items"
    __table_args__ = (
        Index("ix_memory_kb_created_at", "knowledge_base_id", "created_at"),
        Index("ix_memory_kb_expires_at", "knowledge_base_id", "expires_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)  # JSON 字符串
    ttl_seconds = Column(Integer, default=-1)  # -1 表示永久
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    knowledge_base = relationship("KnowledgeBase")
