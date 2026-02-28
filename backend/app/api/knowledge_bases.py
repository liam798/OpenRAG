"""知识库 API"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import get_current_user, has_kb_access, require_kb_write, require_kb_admin, require_kb_owner
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseMember, MemberRole
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    MemberAdd,
    MemberUpdate,
    MemberResponse,
)
from app.schemas.document import DocumentResponse
from app.services.knowledge_base import create_knowledge_base, add_member, update_member_role, remove_member
from app.services.activity import record_activity
from app.models.activity import ActivityAction
from app.rag.pipeline import chunk_and_embed

router = APIRouter(prefix="/knowledge-bases", tags=["知识库"])


def _kb_response(kb: KnowledgeBase, db: Session) -> KnowledgeBaseResponse:
    from app.models.document import Document
    doc_count = db.query(func.count(Document.id)).filter(Document.knowledge_base_id == kb.id).scalar() or 0
    owner = db.query(User).filter(User.id == kb.owner_id).first()
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description or "",
        visibility=kb.visibility,
        owner_id=kb.owner_id,
        owner_username=owner.username if owner else "",
        created_at=kb.created_at.isoformat() if kb.created_at else None,
        document_count=doc_count,
    )


def _get_kb(db: Session, kb_id: int) -> KnowledgeBase | None:
    return db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()


@router.get("", response_model=list[KnowledgeBaseResponse])
def list_my_knowledge_bases(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """我的知识库列表（拥有的 + 有权限的）"""
    # 拥有的
    owned = db.query(KnowledgeBase).filter(KnowledgeBase.owner_id == current_user.id).all()
    # 作为成员的
    member_kbs = (
        db.query(KnowledgeBase)
        .join(KnowledgeBaseMember)
        .filter(KnowledgeBaseMember.user_id == current_user.id)
        .all()
    )
    all_kbs = list({kb.id: kb for kb in owned + member_kbs}.values())
    return [_kb_response(kb, db) for kb in all_kbs]


@router.post("", response_model=KnowledgeBaseResponse)
def create(
    data: KnowledgeBaseCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """创建知识库"""
    kb = create_knowledge_base(db, current_user, data.name, data.description, data.visibility)
    record_activity(db, current_user.id, ActivityAction.CREATE_KB, kb.id, {"name": kb.name})
    return _kb_response(kb, db)


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
def get(
    kb_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """知识库详情"""
    kb = _get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if not has_kb_access(kb, current_user, db):
        raise HTTPException(status_code=403, detail="无访问权限")
    return _kb_response(kb, db)


@router.patch("/{kb_id}", response_model=KnowledgeBaseResponse)
def update(
    kb_id: int,
    data: KnowledgeBaseUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """更新知识库（仅所有者或管理员）"""
    kb = _get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if not require_kb_admin(kb, current_user, db):
        raise HTTPException(status_code=403, detail="需管理员权限")
    if data.name is not None:
        kb.name = data.name
    if data.description is not None:
        kb.description = data.description
    if data.visibility is not None:
        kb.visibility = data.visibility
    db.commit()
    db.refresh(kb)
    return _kb_response(kb, db)


@router.delete("/{kb_id}")
def delete(
    kb_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """删除知识库（仅所有者）"""
    kb = _get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if not require_kb_owner(kb, current_user):
        raise HTTPException(status_code=403, detail="仅所有者可删除")
    from app.rag.vector_store import delete_kb_vectors
    delete_kb_vectors(kb_id)
    db.delete(kb)
    db.commit()
    return {"message": "已删除"}


@router.post("/{kb_id}/documents")
def upload_document(
    kb_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
):
    """上传文档到知识库"""
    kb = _get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if not require_kb_write(kb, current_user, db):
        raise HTTPException(status_code=403, detail="无写权限")

    raw = file.file.read()
    from app.rag.parser import parse_document
    content = parse_document(raw, file.filename or "", file.content_type or "")
    if not content.strip():
        raise HTTPException(status_code=400, detail="文件内容为空或格式不支持")

    from app.models.document import Document
    doc = Document(
        knowledge_base_id=kb_id,
        filename=file.filename or "unknown",
        content_type=file.content_type or "",
        file_size=len(raw),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    chunk_count = chunk_and_embed(kb_id, content, {"document_id": doc.id, "filename": file.filename})
    doc.chunk_count = chunk_count
    db.commit()

    record_activity(
        db, current_user.id, ActivityAction.UPLOAD_DOC, kb_id,
        {"filename": file.filename, "document_id": doc.id},
    )
    return {"document_id": doc.id, "chunk_count": chunk_count}


@router.get("/{kb_id}/documents", response_model=list[DocumentResponse])
def list_documents(
    kb_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """文档列表"""
    kb = _get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if not has_kb_access(kb, current_user, db):
        raise HTTPException(status_code=403, detail="无访问权限")
    from app.models.document import Document
    docs = db.query(Document).filter(Document.knowledge_base_id == kb_id).order_by(Document.created_at.desc()).all()
    return [
        DocumentResponse(
            id=d.id,
            filename=d.filename,
            content_type=d.content_type or "",
            file_size=d.file_size or 0,
            chunk_count=d.chunk_count or 0,
            created_at=d.created_at.isoformat() if d.created_at else None,
        )
        for d in docs
    ]


@router.get("/{kb_id}/members", response_model=list[MemberResponse])
def list_members(
    kb_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """成员列表"""
    kb = _get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if not has_kb_access(kb, current_user, db):
        raise HTTPException(status_code=403, detail="无访问权限")

    members = db.query(KnowledgeBaseMember).filter(KnowledgeBaseMember.knowledge_base_id == kb_id).all()
    result = []
    for m in members:
        u = db.query(User).filter(User.id == m.user_id).first()
        if u:
            result.append(MemberResponse(
                id=m.id,
                user_id=u.id,
                username=u.username,
                email=u.email,
                role=m.role,
                created_at=m.created_at.isoformat() if m.created_at else None,
            ))
    # 添加所有者
    owner = db.query(User).filter(User.id == kb.owner_id).first()
    if owner:
        result.insert(0, MemberResponse(
            id=0,
            user_id=owner.id,
            username=owner.username,
            email=owner.email,
            role=MemberRole.OWNER,
            created_at=kb.created_at.isoformat() if kb.created_at else None,
        ))
    return result


@router.post("/{kb_id}/members", response_model=MemberResponse)
def add_member_endpoint(
    kb_id: int,
    data: MemberAdd,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """添加成员（需管理员权限）"""
    kb = _get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if not require_kb_admin(kb, current_user, db):
        raise HTTPException(status_code=403, detail="需管理员权限")
    if data.user_id == kb.owner_id:
        raise HTTPException(status_code=400, detail="不能修改所有者")
    if data.role == MemberRole.OWNER:
        raise HTTPException(status_code=400, detail="不能直接添加所有者")

    existing = db.query(KnowledgeBaseMember).filter(
        KnowledgeBaseMember.knowledge_base_id == kb_id,
        KnowledgeBaseMember.user_id == data.user_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该用户已是成员")

    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    member = add_member(db, kb, data.user_id, data.role)
    record_activity(
        db, current_user.id, ActivityAction.ADD_MEMBER, kb_id,
        {"member_username": user.username, "role": data.role.value},
    )
    return MemberResponse(
        id=member.id,
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=member.role,
        created_at=member.created_at.isoformat() if member.created_at else None,
    )


@router.patch("/{kb_id}/members/{user_id}", response_model=MemberResponse)
def update_member_endpoint(
    kb_id: int,
    user_id: int,
    data: MemberUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """更新成员角色（需管理员权限）"""
    kb = _get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if not require_kb_admin(kb, current_user, db):
        raise HTTPException(status_code=403, detail="需管理员权限")
    if user_id == kb.owner_id:
        raise HTTPException(status_code=400, detail="不能修改所有者")
    if data.role == MemberRole.OWNER:
        raise HTTPException(status_code=400, detail="不能设置为所有者")

    member = db.query(KnowledgeBaseMember).filter(
        KnowledgeBaseMember.knowledge_base_id == kb_id,
        KnowledgeBaseMember.user_id == user_id,
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")

    member = update_member_role(db, member, data.role)
    u = db.query(User).filter(User.id == user_id).first()
    return MemberResponse(
        id=member.id,
        user_id=u.id,
        username=u.username,
        email=u.email,
        role=member.role,
        created_at=member.created_at.isoformat() if member.created_at else None,
    )


@router.delete("/{kb_id}/members/{user_id}")
def remove_member_endpoint(
    kb_id: int,
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """移除成员（需管理员权限，或用户自己退出）"""
    kb = _get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if user_id == kb.owner_id:
        raise HTTPException(status_code=400, detail="不能移除所有者")

    if current_user.id == user_id:
        # 自己退出
        member = db.query(KnowledgeBaseMember).filter(
            KnowledgeBaseMember.knowledge_base_id == kb_id,
            KnowledgeBaseMember.user_id == user_id,
        ).first()
        if not member:
            raise HTTPException(status_code=404, detail="您不是该知识库成员")
    else:
        if not require_kb_admin(kb, current_user, db):
            raise HTTPException(status_code=403, detail="需管理员权限")
        member = db.query(KnowledgeBaseMember).filter(
            KnowledgeBaseMember.knowledge_base_id == kb_id,
            KnowledgeBaseMember.user_id == user_id,
        ).first()
        if not member:
            raise HTTPException(status_code=404, detail="成员不存在")

    remove_member(db, member)
    return {"message": "已移除"}
