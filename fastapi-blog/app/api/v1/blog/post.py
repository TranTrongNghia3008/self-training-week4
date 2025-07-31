from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.post import PostCreate, PostUpdate, PostOut
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.blog import post_service
from app.workers.tasks import send_notification_email


router = APIRouter()


@router.get("/", response_model=List[PostOut])
def list_posts(db: Session = Depends(get_db)):
    return post_service.get_all_posts(db)


@router.get("/post/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = post_service.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/post/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_post = post_service.create_post(db, post, current_user)

    # Gửi email async
    send_notification_email.delay(
        to_email="admin@example.com",
        subject=f"New Post by {current_user.email}",
        content=f"Title: {new_post.title}\n\n{new_post.content}"
    )

    return new_post


@router.put("/post/{post_id}", response_model=PostOut)
def update_post(post_id: int, post_data: PostUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return post_service.update_post(db, post_id, post_data, current_user)
    except ValueError:
        raise HTTPException(status_code=404, detail="Post not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.delete("/post/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        post_service.delete_post(db, post_id, current_user)
    except ValueError:
        raise HTTPException(status_code=404, detail="Post not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"message": "Post deleted"}
