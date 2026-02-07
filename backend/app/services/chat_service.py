from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.chat import ChatResponse
from app.services.retrieval_service import retrieve_chunks
from app.services.prompt_builder import build_prompt
from app.services.llm_service import generate_answer_safe
from app.core.logger import get_logger
from fastapi import Request
from app.services.gaurds import validate_context_size
import time

CHAT_MAX_LATENCY=20

def chat(
        db:Session,
        user:User,
        query:str,
        top_k:int,
        request:Request
)->ChatResponse:
    
    start=time.time()

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

    chunks=validate_context_size(chunks)

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
    elapsed = time.time() - start
    if elapsed>CHAT_MAX_LATENCY:
        logger.warning("Chat timeout before LLM")
        return ChatResponse(
            query=query,
            answer="The request took too long. Please try again.",
            context_chunks=[]
        )
    
    answer=generate_answer_safe(prompt)

    total_latency = time.time() - start
    # 5. Soft timeout AFTER LLM
    if total_latency > CHAT_MAX_LATENCY:
        logger.warning("Chat timeout after LLM", extra={"latency": total_latency})
        return ChatResponse(
            query=query,
            answer="I found relevant information, but the response took too long to generate.",
            context_chunks=chunks
        )

    return ChatResponse(
        query=query,
        answer=answer,
        context_chunks=chunks
    )