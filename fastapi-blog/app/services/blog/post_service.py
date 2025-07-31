# app/services/blog/post_service.py

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from fastapi import HTTPException
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate
from app.workers.tasks import send_notification_email


def list_posts(search: str, category_id: int, limit: int, offset: int, db: Session):
    query = db.query(Post).options(
        selectinload(Post.author),
        selectinload(Post.comments),
        selectinload(Post.medias),
        selectinload(Post.category)
    )

    if search:
        query = query.filter(or_(
            Post.title.ilike(f"%{search}%"),
            Post.content.ilike(f"%{search}%")
        ))

    if category_id:
        query = query.filter(Post.category_id == category_id)

    return query.offset(offset).limit(limit).all()


def get_post_by_id(post_id: int, db: Session):
    post = db.query(Post)\
        .options(
            selectinload(Post.author),
            selectinload(Post.comments),
            selectinload(Post.medias),
            selectinload(Post.category)
        )\
        .filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


def create_post(post_data: PostCreate, db: Session, current_user: User):
    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        views=0,
        author_id=current_user.id,
        category_id=post_data.category_id
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


def update_post(post_id: int, post_data: PostUpdate, db: Session, current_user: User):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    post.title = post_data.title
    post.content = post_data.content
    post.category = post_data.category_id
    db.commit()
    db.refresh(post)
    return post


def delete_post(post_id: int, db: Session, current_user: User):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(post)
    db.commit()
