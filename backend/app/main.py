from fastapi import FastAPI
from app.core.config import PROJECT_NAME,STORAGE_DIR,DOCUMENTS_DIR
# from app.core.config import DATABASE_URL
from app.api.health import router as router_health
from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.db.session import engine
from app.db.base import Base
from app.api.documents import router as document_router
from app.api.retrieval import router as retrieval_router
from app.api.chat import router as chat_router
from app.core.logging import configure_logging
from app.middleware.request_id import RequestIDMiddleware
import logging
import app.models
from app.core.rate_limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler


#bootstrap
configure_logging()

STORAGE_DIR.mkdir(exist_ok=True)
DOCUMENTS_DIR.mkdir(exist_ok=True)

app = FastAPI(title=PROJECT_NAME)

Base.metadata.create_all(bind=engine)

# middleware
app.add_middleware(RequestIDMiddleware)


# rate limiting
app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)


#routers
app.include_router(router_health, prefix="/v1")
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(document_router)
app.include_router(retrieval_router)
app.include_router(chat_router)

# log noise control
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
