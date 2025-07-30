from pydantic import BaseModel
from datetime import datetime

class MediaBase(BaseModel):
    url: str
    media_type: str

class MediaCreate(BaseModel):
    pass 

class MediaOut(MediaBase):
    id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
