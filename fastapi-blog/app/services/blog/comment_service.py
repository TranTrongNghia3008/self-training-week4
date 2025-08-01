from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreate, CommentUpdate
from app.models.user import User
from app.websockets.comment_manager import comment_manager

def get_comments_by_post(post_id: int, db: Session):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post.comments

async def create_comment(post_id: int, comment: CommentCreate, db: Session, current_user: User):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment = Comment(
        content=comment.content,
        post_id=post.id,
        author_id=current_user.id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

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

async def update_comment(comment_id: int, comment_data: CommentUpdate, db: Session, current_user: User):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")

    comment.content = comment_data.content
    db.commit()
    db.refresh(comment)

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

async def delete_comment(comment_id: int, db: Session, current_user: User):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    db.delete(comment)
    db.commit()

    await comment_manager.broadcast(comment.post_id, {
        "type": "delete_comment",
        "data": {
            "id": comment_id,
        }
    })
    return {"message": "Comment deleted successfully"}
