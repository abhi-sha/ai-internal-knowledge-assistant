from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.security import get_current_user
from app.models.user import User
from app.schemas.retrieval import RetrievalRequest,RetrievelResponse
from app.services.retrieval_service import retrieve_chunks

router=APIRouter(prefix="/retrieval",tags=["Retrieval"])

@router.post("",response_model=RetrievelResponse)
def retrieve(
    payload:RetrievalRequest,
    db:Session=Depends(get_db),
    user:User=Depends(get_current_user)
):
    results=retrieve_chunks(
        db=db,
        user=user,
        query=payload.query,
        top_k=payload.top_k
    )

    return RetrievelResponse(
        query=payload.query,
        results=results)