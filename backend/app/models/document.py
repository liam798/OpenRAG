"""文档模型"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Document(Base):
    """文档表 - 存储上传的文档元数据"""

    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_kb_created_at", "knowledge_base_id", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    filename = Column(String(256), nullable=False)
    content_type = Column(String(64), default="")
    file_size = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
