import uuid
from sqlalchemy import Column,String,Integer,DateTime,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base

class DocumentChunk(Base):
    __tablename__="document_chunks"

    id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    document_id=Column(UUID(as_uuid=True),ForeignKey("documents.id"),nullable=False)
    content=Column(String,nullable=False)
    chunk_index=Column(Integer,nullable=False)

    created_at=Column(DateTime(timezone=True),server_default=func.now())
