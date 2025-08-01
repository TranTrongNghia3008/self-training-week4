from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.media import Media
from app.models.post import Post
from app.models.user import User
from app.core.cloudinary_service import upload_media_to_cloudinary, delete_media_from_cloudinary


async def upload_media(post_id: int, file: UploadFile, db: AsyncSession, current_user: User):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # This is sync because file.file is a SpooledTemporaryFile, not async
    upload_result = upload_media_to_cloudinary(file.file)

    media = Media(
        url=upload_result["url"],
        public_id=upload_result["public_id"],
        media_type=upload_result["media_type"],
        post_id=post_id
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media


async def get_media(media_id: int, db: AsyncSession):
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalars().first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media


async def delete_media(media_id: int, db: AsyncSession, current_user: User):
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalars().first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    await db.refresh(media)

    if media.post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(media)
    await db.commit()
    return {"message": "Media deleted successfully"}


def handle_media_before_delete(mapper, connection, target):
    if target.public_id:
        try:
            delete_media_from_cloudinary(target.public_id, target.media_type)
        except Exception as e:
            print(f"[ERROR] Failed to delete from Cloudinary: {e}")
