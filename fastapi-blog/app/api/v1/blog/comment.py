from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentOut
from app.services.blog import comment_service

router = APIRouter()


@router.get("/post/{post_id}", response_model=List[CommentOut], status_code=status.HTTP_200_OK)
async def get_comments(post_id: int, db: AsyncSession = Depends(get_db)):
    return await comment_service.get_comments_by_post(post_id, db)


@router.post("/post/{post_id}", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await comment_service.create_comment(post_id, comment, db, current_user)


@router.put("/{comment_id}", response_model=CommentOut)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await comment_service.update_comment(comment_id, comment_data, db, current_user)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await comment_service.delete_comment(comment_id, db, current_user)
    return {"message": "Comment deleted"}
