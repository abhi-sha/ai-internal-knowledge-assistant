from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest,TokenResponse
from app.auth.security import verify_password,create_access_token

router=APIRouter(prefix="/auth",tags=["auth"])

@router.post("/login",response_model=TokenResponse)
def login(data:LoginRequest,db:Session=Depends(get_db)):

    user=db.query(User).filter(User.email==data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentails"
        )

    if not verify_password(data.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )        
    
    token=create_access_token(
        data={
            "sub":str(user.id),
            "email":user.email,
            "role":user.role
        }
    )

    return {"access_token":token}

