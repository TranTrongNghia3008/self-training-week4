from pydantic import BaseModel
from typing import List, Optional
from .user import UserOut
from .media import MediaOut
from .comment import CommentOut

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostOut(PostBase):
    id: int
    author: UserOut
    media_items: List[MediaOut] = []
    comments: List[CommentOut] = []

    class Config:
        orm_mode = True
