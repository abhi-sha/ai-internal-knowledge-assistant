from uuid import UUID
from pydantic import BaseModel
from typing import List


class RetrievalRequest(BaseModel):
    query:str
    top_k:int=5

class RetrievedChunk(BaseModel):
    document_id:UUID
    chunk_index:int
    content:str
    score:float

class RetrievelResponse(BaseModel):
    query:str
    results:List[RetrievedChunk]
