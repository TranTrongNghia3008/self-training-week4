from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate
from app.workers.tasks import send_notification_email


async def list_posts(search: str, category_id: int, limit: int, offset: int, db: AsyncSession):
    stmt = select(Post).options(
        selectinload(Post.author),
        selectinload(Post.comments),
        selectinload(Post.medias),
        selectinload(Post.category)
    )

    if search:
        stmt = stmt.filter(or_(
            Post.title.ilike(f"%{search}%"),
            Post.content.ilike(f"%{search}%")
        ))

    if category_id:
        stmt = stmt.filter(Post.category_id == category_id)

    result = await db.execute(stmt.offset(offset).limit(limit))
    return result.scalars().all()


async def get_post_by_id(post_id: int, db: AsyncSession):
    stmt = select(Post).options(
        selectinload(Post.author),
        selectinload(Post.comments),
        selectinload(Post.medias),
        selectinload(Post.category)
    ).filter(Post.id == post_id)

    result = await db.execute(stmt)
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


async def create_post(post_data: PostCreate, db: AsyncSession, current_user: User):
    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        views=0,
        author_id=current_user.id,
        category_id=post_data.category_id
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    send_notification_email.delay(
        to_email="admin@example.com",
        subject=f"New Post by {current_user.email}",
        content=f"Title: {new_post.title}\n\n{new_post.content}"
    )

    return new_post


async def update_post(post_id: int, post_data: PostUpdate, db: AsyncSession, current_user: User):
    stmt = select(Post).filter(Post.id == post_id)
    result = await db.execute(stmt)
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    post.title = post_data.title
    post.content = post_data.content
    post.category_id = post_data.category_id
    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(post_id: int, db: AsyncSession, current_user: User):
    stmt = select(Post).filter(Post.id == post_id)
    result = await db.execute(stmt)
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(post)
    await db.commit()
