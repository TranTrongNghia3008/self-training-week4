import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv() 

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    SQLALCHEMY_DATABASE_URI: str
    TEST_DATABASE_URL: str 

    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    REDIS_BROKER_URL: str = "redis://redis:6379/0"
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    class Config:
        env_file = ".env"

settings = Settings()
