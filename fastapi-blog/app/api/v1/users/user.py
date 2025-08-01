from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut, Token, RefreshTokenRequest, MessageResponse
from app.services.users.user_service import (
    register_user, authenticate_user,
    refresh_user_token, logout_user
)

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(user, db)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    return await authenticate_user(form_data.username, form_data.password, db)

@router.post("/refresh", response_model=Token)
async def refresh(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    return await refresh_user_token(data, db)

@router.post("/logout", response_model=MessageResponse)
async def logout(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    await logout_user(data, db)
    return MessageResponse(message="Logout successful")
