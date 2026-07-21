import uuid
from datetime import datetime

from pydantic import BaseModel


class SessionDocumentItem(BaseModel):
    document_id: uuid.UUID
    document_title: str | None
    created_date: datetime

    model_config = {"from_attributes": True}
