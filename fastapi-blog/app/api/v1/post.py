from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.post import PostCreate, PostUpdate, PostOut
from app.models.post import Post
from app.models.user import User
from app.core.dependencies import get_current_user  

router = APIRouter()

# GET all posts
@router.get("/", response_model=List[PostOut])
def list_posts(db: Session = Depends(get_db)):
    return db.query(Post).all()

# GET post by ID
@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# POST create new post
@router.post("/", response_model=PostOut)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_post = Post(
        title=post.title,
        content=post.content,
        author_id=current_user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# PUT update post
@router.put("/{post_id}", response_model=PostOut)
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

# DELETE post
@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}
