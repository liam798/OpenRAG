"""活动记录服务"""
import json
from sqlalchemy.orm import Session

from app.models.activity import Activity, ActivityAction


def record_activity(
    db: Session,
    user_id: int,
    action: ActivityAction,
    knowledge_base_id: int | None = None,
    extra: dict | None = None,
) -> Activity:
    """记录一条活动"""
    a = Activity(
        user_id=user_id,
        action=action,
        knowledge_base_id=knowledge_base_id,
        extra=json.dumps(extra, ensure_ascii=False) if extra else None,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a
