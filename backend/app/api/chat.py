from fastapi import APIRouter,Depends,Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.security import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest,ChatResponse
from app.services.chat_service import chat
from app.core.rate_limiter import limiter

router= APIRouter(prefix="/chat",tags=["chat"])


@router.post("",response_model=ChatResponse)
@limiter.limit("10/minute")
def chat_endpoint(
    request:Request,
    payload:ChatRequest,
    db:Session=Depends(get_db),
    user:User=Depends(get_current_user),

):
    
    return chat(
        request=request,
        db=db,
        user=user,
        query=payload.query,
        top_k=payload.top_k,
    )

