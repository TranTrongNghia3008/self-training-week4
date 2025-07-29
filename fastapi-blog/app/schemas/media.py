from pydantic import BaseModel

class MediaBase(BaseModel):
    file_url: str
    file_type: str  # image or video

class MediaCreate(MediaBase):
    pass

class MediaOut(MediaBase):
    id: int

    class Config:
        orm_mode = True
