import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

PROJECT_NAME = os.getenv("PROJECT_NAME")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))
BASE_DIR=Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage"
DOCUMENTS_DIR = STORAGE_DIR / "documents"
VECTOR_DIMENSION = 384  # all-MiniLM-L6-v2
VECTOR_STORE_PATH = "storage/vector_store/index.faiss"
METADATA_PATH = "storage/vector_store/metadata.pkl"
