from datetime import datetime

from pydantic import BaseModel

from app.models.enums import NotificationType


class NotificationRead(BaseModel):
    id: str
    type: NotificationType
    title: str
    message: str
    payload: dict | None = None
    read_at: datetime | None = None
    created_at: datetime

