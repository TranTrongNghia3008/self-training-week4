from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # image, video, etc.
    post_id = Column(Integer, ForeignKey("posts.id"))

    post = relationship("Post", back_populates="medias")
