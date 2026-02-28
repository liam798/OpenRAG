"""RAG 问答 API"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, has_kb_access
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseMember
from app.schemas.rag import QueryRequest, QueryResponse, BatchQueryRequest
from app.rag.pipeline import query_kb, query_kbs

router = APIRouter(tags=["RAG 问答"])


def _get_kb(db: Session, kb_id: int) -> KnowledgeBase | None:
    return db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()


def _get_accessible_kb_ids(db: Session, user: User) -> list[int]:
    """获取用户可访问的知识库 ID 列表（拥有的 + 成员的 + 公开的）"""
    owned = db.query(KnowledgeBase.id).filter(KnowledgeBase.owner_id == user.id).all()
    member_kbs = (
        db.query(KnowledgeBase.id)
        .join(KnowledgeBaseMember)
        .filter(KnowledgeBaseMember.user_id == user.id)
        .all()
    )
    from app.models.knowledge_base import Visibility
    public = db.query(KnowledgeBase.id).filter(KnowledgeBase.visibility == Visibility.PUBLIC).all()
    seen = set()
    result = []
    for (kb_id,) in owned + member_kbs + public:
        if kb_id not in seen:
            seen.add(kb_id)
            kb = _get_kb(db, kb_id)
            if kb and has_kb_access(kb, user, db):
                result.append(kb_id)
    return result


@router.post("/knowledge-bases/query", response_model=QueryResponse)
def batch_query(
    data: BatchQueryRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """多知识库 RAG 问答，kb_ids 为空时表示全部可访问知识库"""
    kb_ids = data.kb_ids if data.kb_ids else _get_accessible_kb_ids(db, current_user)
    for kb_id in kb_ids:
        kb = _get_kb(db, kb_id)
        if not kb or not has_kb_access(kb, current_user, db):
            raise HTTPException(status_code=403, detail=f"无权限访问知识库 {kb_id}")
    if not kb_ids:
        raise HTTPException(status_code=400, detail="暂无可用知识库，请先创建或加入知识库")
    answer, sources = query_kbs(kb_ids, data.question, data.top_k)
    return QueryResponse(answer=answer, sources=sources)


@router.post("/knowledge-bases/{kb_id}/query", response_model=QueryResponse)
def query(
    kb_id: int,
    data: QueryRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """基于知识库的 RAG 问答"""
    kb = _get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if not has_kb_access(kb, current_user, db):
        raise HTTPException(status_code=403, detail="无访问权限")

    answer, sources = query_kb(kb_id, data.question, data.top_k)
    return QueryResponse(answer=answer, sources=sources)
