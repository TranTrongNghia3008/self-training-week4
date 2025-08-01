from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.schemas.post import PostCreate, PostUpdate, PostOut
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.blog import post_service

router = APIRouter()


@router.get("/", response_model=List[PostOut])
async def list_posts(
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await post_service.list_posts(search, category_id, limit, offset, db)


@router.get("/post/{post_id}", response_model=PostOut)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    return await post_service.get_post_by_id(post_id, db)


@router.post("/post/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await post_service.create_post(post, db, current_user)


@router.put("/post/{post_id}", response_model=PostOut)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await post_service.update_post(post_id, post_data, db, current_user)


@router.delete("/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await post_service.delete_post(post_id, db, current_user)
    return {"message": "Post deleted"}
