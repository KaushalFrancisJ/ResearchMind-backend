import uuid
from datetime import datetime

from pydantic import BaseModel


class SessionCreate(BaseModel):
    session_title: str


class SessionResponse(BaseModel):
    session_id: uuid.UUID
    session_title: str | None
    last_active: datetime

    model_config = {"from_attributes": True}
