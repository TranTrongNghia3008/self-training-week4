from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreate, CommentUpdate
from app.models.user import User
from app.websockets.comment_manager import comment_manager


async def get_comments_by_post(post_id: int, db: AsyncSession):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.refresh(post)
    return post.comments


async def create_comment(post_id: int, comment: CommentCreate, db: AsyncSession, current_user: User):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment = Comment(
        content=comment.content,
        post_id=post.id,
        author_id=current_user.id
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    await comment_manager.broadcast(post_id, {
        "type": "new_comment",
        "data": {
            "id": new_comment.id,
            "content": new_comment.content,
            "author": current_user.id,
            "post_id": new_comment.post_id
        }
    })

    return new_comment


async def update_comment(comment_id: int, comment_data: CommentUpdate, db: AsyncSession, current_user: User):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")

    comment.content = comment_data.content
    await db.commit()
    await db.refresh(comment)

    await comment_manager.broadcast(comment.post_id, {
        "type": "update_comment",
        "data": {
            "id": comment.id,
            "content": comment.content,
            "author": current_user.id,
            "post_id": comment.post_id
        }
    })

    return comment


async def delete_comment(comment_id: int, db: AsyncSession, current_user: User):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    await db.delete(comment)
    await db.commit()

    await comment_manager.broadcast(comment.post_id, {
        "type": "delete_comment",
        "data": {
            "id": comment_id,
        }
    })

    return {"message": "Comment deleted successfully"}
