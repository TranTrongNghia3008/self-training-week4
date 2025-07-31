from sqlalchemy.orm import Session
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


def register_user(user_data: UserCreate, db: Session) -> User:
    existing = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(username: str, password: str, db: Session) -> Token:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(db, user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


def refresh_user_token(data: RefreshTokenRequest, db: Session) -> Token:
    try:
        payload = jwt.decode(data.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    db_token = db.query(RefreshToken).filter(RefreshToken.token == data.refresh_token).first()
    if not db_token or db_token.revoked or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

    db_token.revoked = True
    db.commit()

    access_token = create_access_token(data={"sub": str(user_id)})
    new_refresh_token = create_refresh_token(db, user_id)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


def logout_user(data: RefreshTokenRequest, db: Session):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == data.refresh_token).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")

    db_token.revoked = True
    db.commit()
