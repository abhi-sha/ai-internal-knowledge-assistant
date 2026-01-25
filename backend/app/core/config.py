import os
from dotenv import load_dotenv


load_dotenv()

PROJECT_NAME = os.getenv("PROJECT_NAME")
DATABASE_URL = os.getenv("DATABASE_URL")
