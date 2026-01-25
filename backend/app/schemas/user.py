from pydantic import BaseModel,EmailStr
from uuid import UUID

class UserCreate(BaseModel):
    email:EmailStr
    password:str
    role:str

class UserResponse(BaseModel):
    id:UUID
    email:EmailStr
    role:str