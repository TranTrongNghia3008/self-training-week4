from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from jose import jwt, JWTError
from fastapi import HTTPException

from app.models.user import User
from app.models.token import RefreshToken
from app.schemas.user import UserCreate, RefreshTokenRequest, Token
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token
)
from app.core.config import settings


async def register_user(user_data: UserCreate, db: AsyncSession) -> User:
    result = await db.execute(
        select(User).where((User.email == user_data.email) | (User.username == user_data.username))
    )
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def authenticate_user(username: str, password: str, db: AsyncSession) -> Token:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = await create_refresh_token(db, user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


async def refresh_user_token(data: RefreshTokenRequest, db: AsyncSession) -> Token:
    try:
        payload = jwt.decode(data.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(RefreshToken).where(RefreshToken.token == data.refresh_token))
    db_token = result.scalars().first()
    if not db_token or db_token.revoked or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

    db_token.revoked = True
    await db.commit()

    access_token = create_access_token(data={"sub": str(user_id)})
    new_refresh_token = await create_refresh_token(db, user_id)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


async def logout_user(data: RefreshTokenRequest, db: AsyncSession):
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == data.refresh_token))
    db_token = result.scalars().first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")

    db_token.revoked = True
    await db.commit()
