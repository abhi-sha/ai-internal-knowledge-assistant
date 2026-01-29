from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.chat import ChatResponse
from app.services.retrieval_service import retrieve_chunks
from app.services.prompt_builder import build_prompt
from app.services.llm_service import generate_answer


def chat(
        db:Session,
        user:User,
        query:str,
        top_k:int
)->ChatResponse:
    

    #1. Retrieve chunks
    chunks=retrieve_chunks(
        db=db,
        user=user,
        query=query,
        top_k=top_k
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