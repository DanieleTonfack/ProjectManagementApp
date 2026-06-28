from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import ActivityLog, Notification
from app.models.enums import ActivityType, NotificationType


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def log_activity(
    db: Session,
    *,
    actor_id: str | None,
    type: ActivityType,
    title: str,
    project_id: str | None = None,
    task_id: str | None = None,
    details: dict | None = None,
) -> ActivityLog:
    entry = ActivityLog(
        actor_id=actor_id,
        type=type,
        title=title,
        project_id=project_id,
        task_id=task_id,
        details=details,
    )
    db.add(entry)
    return entry


def create_notification(
    db: Session,
    *,
    user_id: str,
    type: NotificationType,
    title: str,
    message: str,
    payload: dict | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        payload=payload,
    )
    db.add(notification)
    return notification

