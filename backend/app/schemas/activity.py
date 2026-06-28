from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ActivityType


class ActivityRead(BaseModel):
    id: str
    type: ActivityType
    title: str
    details: dict | None = None
    project_id: str | None = None
    task_id: str | None = None
    created_at: datetime

