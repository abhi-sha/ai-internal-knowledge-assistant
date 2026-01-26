from fastapi import FastAPI
from app.core.config import PROJECT_NAME
# from app.core.config import DATABASE_URL
from app.api.health import router as router_health
from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.db.session import engine
from app.db.base import Base
from app.api.documents import router as document_router
import app.models


app = FastAPI(title=PROJECT_NAME)

Base.metadata.create_all(bind=engine)
app.include_router(router_health, prefix="/v1")
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(document_router)
