"""知识库模型 - 类似 GitHub 仓库"""
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Visibility(str, enum.Enum):
    """知识库可见性"""
    PUBLIC = "public"
    PRIVATE = "private"


class MemberRole(str, enum.Enum):
    """成员角色 - 类似 GitHub 权限"""
    OWNER = "owner"    # 所有者，可删除、转让
    ADMIN = "admin"    # 管理员，可管理成员
    WRITE = "write"    # 可写，可上传文档
    READ = "read"      # 只读，可查询


class KnowledgeBase(Base):
    """知识库表 - 类似 GitHub 仓库"""

    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, default="")
    visibility = Column(Enum(Visibility, values_callable=lambda x: [e.value for e in x]), default=Visibility.PRIVATE)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    owner = relationship("User", back_populates="owned_knowledge_bases", foreign_keys=[owner_id])
    members = relationship("KnowledgeBaseMember", back_populates="knowledge_base", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="knowledge_base")


class KnowledgeBaseMember(Base):
    """知识库成员表 - 权限管理"""

    __tablename__ = "knowledge_base_members"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(MemberRole, values_callable=lambda x: [e.value for e in x]), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="members")
    user = relationship("User", back_populates="memberships")
