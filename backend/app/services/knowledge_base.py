"""知识库服务"""
from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseMember, MemberRole, Visibility
from app.models.user import User


def create_knowledge_base(db, owner: User, name: str, description: str = "", visibility: Visibility = Visibility.PRIVATE) -> KnowledgeBase:
    """创建知识库"""
    kb = KnowledgeBase(
        name=name,
        description=description,
        visibility=visibility,
        owner_id=owner.id,
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb


def add_member(db, kb: KnowledgeBase, user_id: int, role: MemberRole) -> KnowledgeBaseMember:
    """添加成员"""
    member = KnowledgeBaseMember(
        knowledge_base_id=kb.id,
        user_id=user_id,
        role=role,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def update_member_role(db, member: KnowledgeBaseMember, role: MemberRole) -> KnowledgeBaseMember:
    """更新成员角色"""
    member.role = role
    db.commit()
    db.refresh(member)
    return member


def remove_member(db, member: KnowledgeBaseMember) -> None:
    """移除成员"""
    db.delete(member)
    db.commit()
