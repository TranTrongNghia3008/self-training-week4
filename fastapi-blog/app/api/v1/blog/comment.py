from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentOut
from app.services.blog import comment_service

router = APIRouter()

@router.get("/post/{post_id}", response_model=List[CommentOut], status_code=status.HTTP_200_OK)
def get_comments(post_id: int, db: Session = Depends(get_db)):
    return comment_service.get_comments_by_post(post_id, db)

@router.post("/post/{post_id}", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(post_id: int, comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return comment_service.create_comment(post_id, comment, db, current_user)

@router.put("/{comment_id}", response_model=CommentOut)
def update_comment(comment_id: int, comment_data: CommentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return comment_service.update_comment(comment_id, comment_data, db, current_user)

@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return comment_service.delete_comment(comment_id, db, current_user)
