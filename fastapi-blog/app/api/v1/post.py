from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.post import PostCreate, PostOut
from app.models.post import Post
from app.api.deps import get_db

router = APIRouter()

@router.post("/", response_model=PostOut)
def create_post(post_in: PostCreate, db: Session = Depends(get_db)):
    post = Post(title=post_in.title, content=post_in.content, author_id=1)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post
