from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings
from sqlalchemy.orm import Session
from app.models.token import RefreshToken

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded

def create_refresh_token(db: Session, user_id: int):
    expire = datetime.utcnow() + timedelta(days=7)
    payload = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    db_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expire,
        revoked=False
    )
    db.add(db_token)
    db.commit()
    return token

def verify_password(plain_password: str, hashed_password: str):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)   