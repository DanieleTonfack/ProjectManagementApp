from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import ActivityLog, Notification, Project, ProjectMember, Task, User
from app.models.enums import ProjectStatus, TaskStatus

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project_ids = (
        db.query(Project.id)
        .outerjoin(ProjectMember, ProjectMember.project_id == Project.id)
        .filter(or_(Project.owner_id == current_user.id, ProjectMember.user_id == current_user.id))
        .subquery()
    )

    active_projects = db.query(func.count(Project.id)).filter(Project.id.in_(project_ids), Project.status == ProjectStatus.active).scalar() or 0
    assigned_tasks = db.query(func.count(Task.id)).filter(Task.assignee_id == current_user.id).scalar() or 0
    overdue_tasks = (
        db.query(func.count(Task.id))
        .filter(Task.assignee_id == current_user.id, Task.status != TaskStatus.done, Task.due_date.isnot(None), Task.due_date < datetime.now(timezone.utc))
        .scalar()
        or 0
    )
    unread_notifications = (
        db.query(func.count(Notification.id))
        .filter(Notification.user_id == current_user.id, Notification.read_at.is_(None))
        .scalar()
        or 0
    )

    recent_projects = (
        db.query(Project)
        .outerjoin(ProjectMember, ProjectMember.project_id == Project.id)
        .filter(or_(Project.owner_id == current_user.id, ProjectMember.user_id == current_user.id))
        .order_by(Project.updated_at.desc())
        .limit(5)
        .all()
    )
    recent_tasks = (
        db.query(Task)
        .filter(or_(Task.assignee_id == current_user.id, Task.created_by_id == current_user.id))
        .order_by(Task.updated_at.desc())
        .limit(5)
        .all()
    )
    recent_notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(5)
        .all()
    )
    recent_activity = (
        db.query(ActivityLog)
        .filter(or_(ActivityLog.actor_id == current_user.id, ActivityLog.project_id.in_(project_ids)))
        .order_by(ActivityLog.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "active_projects": active_projects,
        "assigned_tasks": assigned_tasks,
        "overdue_tasks": overdue_tasks,
        "unread_notifications": unread_notifications,
        "recent_projects": [
            {"id": item.id, "name": item.name, "description": item.description, "updated_at": item.updated_at}
            for item in recent_projects
        ],
        "recent_tasks": [
            {"id": item.id, "project_id": item.project_id, "title": item.title, "status": item.status, "priority": item.priority, "updated_at": item.updated_at}
            for item in recent_tasks
        ],
        "recent_notifications": [
            {"id": item.id, "title": item.title, "message": item.message, "read_at": item.read_at, "created_at": item.created_at}
            for item in recent_notifications
        ],
        "recent_activity": [
            {"id": item.id, "type": item.type, "title": item.title, "created_at": item.created_at}
            for item in recent_activity
        ],
        "generated_at": datetime.now(timezone.utc),
    }
