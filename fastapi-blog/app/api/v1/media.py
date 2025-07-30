from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import event
from app.db.session import get_db
from app.models.media import Media
from app.models.post import Post
from app.models.user import User
from app.core.dependencies import get_current_user
from app.core.cloudinary_service import delete_media_from_cloudinary
from app.core.cloudinary_service import upload_media_to_cloudinary
from app.schemas.media import MediaOut

router = APIRouter()

@router.post("/upload/{post_id}", response_model=MediaOut)
def upload_media(post_id: int,
                 file: UploadFile = File(...),
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    upload_result = upload_media_to_cloudinary(file.file)

    media = Media(
        url=upload_result["url"],
        public_id=upload_result["public_id"],
        media_type=upload_result["media_type"],
        post_id=post_id
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media

@router.get("/{media_id}", response_model=MediaOut)
def get_media(media_id: int, db: Session = Depends(get_db)):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media

@router.delete("/{media_id}")
def delete_media(media_id: int,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if media.post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(media)
    db.commit()
    return {"message": "Media deleted successfully"}

@event.listens_for(Media, "before_delete")
def delete_media_file(mapper, connection, target):
    if target.public_id:
        try:
            delete_media_from_cloudinary(target.public_id, target.media_type)
        except Exception as e:
            print(f"[ERROR] Failed to delete from Cloudinary: {e}")