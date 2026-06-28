from datetime import datetime

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    active_projects: int
    assigned_tasks: int
    overdue_tasks: int
    unread_notifications: int
    recent_projects: list[dict]
    recent_tasks: list[dict]
    recent_notifications: list[dict]
    recent_activity: list[dict]
    generated_at: datetime

