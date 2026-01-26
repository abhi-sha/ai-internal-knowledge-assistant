from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id:UUID
    filename:str
    content_type:str
    uploaded_by:UUID
    created_at:datetime

    class Config:
        from_attributes=True