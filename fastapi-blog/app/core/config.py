import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()  # Load from .env

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SQLALCHEMY_DATABASE_URI: str
    class Config:
        env_file = ".env"

settings = Settings()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30