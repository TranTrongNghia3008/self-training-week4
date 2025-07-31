from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, selectinload
from typing import List
from fastapi import status
from app.db.session import get_db
from app.schemas.post import PostCreate, PostUpdate, PostOut
from app.models.post import Post
from app.models.user import User
from app.core.dependencies import get_current_user  
from app.workers.tasks import send_notification_email


router = APIRouter()

@router.get("/", response_model=List[PostOut])
def list_posts(db: Session = Depends(get_db)):
    return db.query(Post)\
        .options(
            selectinload(Post.author),
            selectinload(Post.comments),
            selectinload(Post.medias)
        ).all()

@router.get("/post/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post)\
        .options(
            selectinload(Post.author),
            selectinload(Post.comments),
            selectinload(Post.medias)
        )\
        .filter(Post.id == post_id)\
        .first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.post("/post/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_post = Post(
        title=post.title,
        content=post.content,
        author_id=current_user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    send_notification_email.delay(
        to_email="admin@example.com",
        subject=f"New Post by {current_user.email}",
        content=f"Title: {new_post.title}\n\n{new_post.content}"
    )

    return new_post

@router.put("/post/{post_id}", response_model=PostOut)
def update_post(post_id: int, post_data: PostUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    post.title = post_data.title
    post.content = post_data.content
    db.commit()
    db.refresh(post)
    return post

@router.delete("/post/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}
