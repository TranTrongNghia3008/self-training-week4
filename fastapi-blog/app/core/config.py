import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env

class Settings:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

settings = Settings()
