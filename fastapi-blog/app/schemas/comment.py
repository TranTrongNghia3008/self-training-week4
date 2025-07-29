from pydantic import BaseModel
from .user import UserOut

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentOut(CommentBase):
    id: int
    author: UserOut

    class Config:
        orm_mode = True
