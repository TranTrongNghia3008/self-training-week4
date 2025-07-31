from pydantic import BaseModel
from typing import List, Optional
from .user import UserOut
from .media import MediaOut
from .comment import CommentOut
from .category import CategoryOut

class PostBase(BaseModel):
    title: str
    content: str
    category_id: Optional[int]

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase): 
    pass

class PostOut(PostBase):
    id: int
    author: UserOut
    content: str
    views: int
    category: Optional[CategoryOut]
    medias: List[MediaOut] = []
    comments: List[CommentOut] = []

    class Config:
        from_attributes = True
