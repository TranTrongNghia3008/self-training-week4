from fastapi import APIRouter, UploadFile, File, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import event

from app.db.session import get_db
from app.models.media import Media
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.media import MediaOut
from app.services.blog import media_service

router = APIRouter()

@router.post("/upload/{post_id}", response_model=MediaOut, status_code=status.HTTP_201_CREATED)
async def upload_media(
    post_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await media_service.upload_media(post_id, file, db, current_user)


@router.get("/{media_id}", response_model=MediaOut)
async def get_media(
    media_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await media_service.get_media(media_id, db)


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await media_service.delete_media(media_id, db, current_user)
    return {"message": "Media deleted"}

@event.listens_for(Media, "before_delete")
def delete_media_file(mapper, connection, target):
    media_service.handle_media_before_delete(mapper, connection, target)
