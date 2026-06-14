import uuid
from datetime import datetime

from pydantic import BaseModel


class SessionCreate(BaseModel):
    session_title: str | None = None


class SessionResponse(BaseModel):
    session_id: uuid.UUID
    session_title: str | None
    created_date: datetime
    updated_date: datetime

    model_config = {"from_attributes": True}
