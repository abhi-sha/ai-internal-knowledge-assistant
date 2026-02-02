from fastapi import APIRouter,Depends,HTTPException,status,Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest,TokenResponse
from app.auth.security import verify_password,create_access_token,get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from app.core.rate_limiter import limiter

router=APIRouter(prefix="/auth",tags=["auth"])

@router.post("/login",response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request:Request,data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):

    user=db.query(User).filter(User.email==data.username).first()

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

@router.get("/me")
def read_me(current_user:User=Depends(get_current_user)):
    return{
        "id":current_user.id,
        "email":current_user.email,
        "role":current_user.role   
    }
