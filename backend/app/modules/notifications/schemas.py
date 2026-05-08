from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    """A single notification item."""

    id: UUID
    user_id: UUID
    type: str
    title: str
    body: str | None = None
    link: str | None = None
    is_read: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationCountResponse(BaseModel):
    """Unread notification count."""

    count: int
