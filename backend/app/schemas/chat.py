from pydantic import BaseModel
from typing import List
from app.schemas.retrieval import RetrievedChunk



class ChatRequest(BaseModel):

    query:str
    top_k:int=5

class ChatResponse(BaseModel):
    query:str
    answer:str
    context_chunks:List[RetrievedChunk]

