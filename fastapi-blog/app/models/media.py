from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    public_id = Column(String, nullable=False) 
    media_type = Column(String, nullable=False) 
    post_id = Column(Integer, ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="medias")
