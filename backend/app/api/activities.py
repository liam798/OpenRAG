"""活动/动态 API"""
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, has_kb_access
from app.models.user import User
from app.models.activity import Activity
from app.models.knowledge_base import KnowledgeBase
from app.schemas.activity import ActivityResponse

router = APIRouter(prefix="/activities", tags=["活动"])


def _activity_response(a: Activity, db: Session) -> ActivityResponse:
    import json
    from app.schemas.activity import ACTION_LABELS
    kb_name = None
    kb_owner = None
    if a.knowledge_base_id:
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == a.knowledge_base_id).first()
        if kb:
            kb_name = kb.name
            owner = db.query(User).filter(User.id == kb.owner_id).first()
            kb_owner = owner.username if owner else None
    extra = None
    if a.extra:
        try:
            extra = json.loads(a.extra)
        except Exception:
            pass
    return ActivityResponse(
        id=a.id,
        user_id=a.user_id,
        username=a.user.username,
        action=a.action.value,
        action_label=ACTION_LABELS.get(a.action.value, a.action.value),
        knowledge_base_id=a.knowledge_base_id,
        knowledge_base_name=kb_name,
        knowledge_base_owner=kb_owner,
        extra=extra,
        created_at=a.created_at.isoformat() if a.created_at else "",
    )


@router.get("", response_model=list[ActivityResponse])
def list_activities(
    scope: Annotated[Literal["all", "mine"], Query(description="all=全部动态, mine=我的动态")] = "all",
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """活动列表，支持筛选全部/我的动态"""
    q = db.query(Activity).order_by(Activity.created_at.desc()).limit(limit * 2)  # 多取一些以便过滤
    if scope == "mine":
        q = q.filter(Activity.user_id == current_user.id)
    activities = q.all()
    # 全部动态时只显示用户有权限的知识库相关活动
    if scope == "all":
        filtered = []
        for a in activities:
            if a.knowledge_base_id is None:
                filtered.append(a)
            else:
                kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == a.knowledge_base_id).first()
                if kb and has_kb_access(kb, current_user, db):
                    filtered.append(a)
            if len(filtered) >= limit:
                break
        activities = filtered[:limit]
    else:
        activities = activities[:limit]
    return [_activity_response(a, db) for a in activities]
