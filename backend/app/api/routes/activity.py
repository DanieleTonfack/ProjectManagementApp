from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import ActivityLog, Project, ProjectMember, User

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("")
def list_activity(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    accessible_project_ids = (
        db.query(Project.id)
        .outerjoin(ProjectMember, ProjectMember.project_id == Project.id)
        .filter(or_(Project.owner_id == current_user.id, ProjectMember.user_id == current_user.id))
        .subquery()
    )

    activities = (
        db.query(ActivityLog)
        .filter(or_(ActivityLog.actor_id == current_user.id, ActivityLog.project_id.in_(accessible_project_ids)))
        .order_by(ActivityLog.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": item.id,
            "type": item.type,
            "title": item.title,
            "details": item.details,
            "project_id": item.project_id,
            "task_id": item.task_id,
            "created_at": item.created_at,
        }
        for item in activities
    ]

