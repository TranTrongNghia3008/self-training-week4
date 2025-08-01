# app/db/session.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from typing import AsyncGenerator

# Tạo async engine
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,  # ví dụ: "postgresql+asyncpg://user:pass@localhost/db"
    echo=True,
    future=True
)

# Tạo async session
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Dependency injection dùng trong FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
