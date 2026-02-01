from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.chat import ChatResponse
from app.services.retrieval_service import retrieve_chunks
from app.services.prompt_builder import build_prompt
from app.services.llm_service import generate_answer
from app.core.logger import get_logger
from fastapi import Request

def chat(
        db:Session,
        user:User,
        query:str,
        top_k:int,
        request:Request
)->ChatResponse:
    
    logger = get_logger(
        request_id=request.state.request_id,
        user_id=str(user.id),
        role=user.role
    )

   
    
    #1. Retrieve chunks
    chunks=retrieve_chunks(
        db=db,
        user=user,
        query=query,
        top_k=top_k,
        request=request
    )

    logger.info(
    "Chat request",
    extra={
        "query_length": len(query),
        "context_chunks": len(chunks)
    }
)
    #2. Build prompt

    prompt=build_prompt(
        query=query,
        chunks=chunks
    )

    #3. generate answer

    answer=generate_answer(prompt)



    return ChatResponse(
        query=query,
        answer=answer,
        context_chunks=chunks
    )