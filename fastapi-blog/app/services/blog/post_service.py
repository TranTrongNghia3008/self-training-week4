# app/services/blog/post_service.py

from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate
from app.models.user import User


def get_all_posts(db: Session) -> List[Post]:
    return db.query(Post)\
        .options(
            selectinload(Post.author),
            selectinload(Post.comments),
            selectinload(Post.medias)
        ).all()


def get_post_by_id(db: Session, post_id: int) -> Optional[Post]:
    return db.query(Post)\
        .options(
            selectinload(Post.author),
            selectinload(Post.comments),
            selectinload(Post.medias)
        )\
        .filter(Post.id == post_id)\
        .first()


def create_post(db: Session, post_data: PostCreate, current_user: User) -> Post:
    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        views=0,
        author_id=current_user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


def update_post(db: Session, post_id: int, post_data: PostUpdate, current_user: User) -> Post:
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise ValueError("Post not found")
    if post.author_id != current_user.id:
        raise PermissionError("Not authorized")

    post.title = post_data.title
    post.content = post_data.content
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: int, current_user: User) -> None:
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise ValueError("Post not found")
    if post.author_id != current_user.id:
        raise PermissionError("Not authorized")
    db.delete(post)
    db.commit()
