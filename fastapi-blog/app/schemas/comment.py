from pydantic import BaseModel
from datetime import datetime


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass


class CommentOut(CommentBase):
    id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True
