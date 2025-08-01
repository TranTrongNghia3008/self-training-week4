from fastapi import APIRouter
from app.api.v1.users import user
from app.api.v1.blog import post, comment, media, category
from app.api.v1.notifications import email 
from app.api.v1.websockets import comment_ws

router = APIRouter()

router.include_router(user.router, prefix="/users", tags=["Users"])
router.include_router(post.router, prefix="/blog", tags=["Posts"])
router.include_router(comment.router, prefix="/blog/comments", tags=["Comments"])
router.include_router(media.router, prefix="/blog/media", tags=["Media"])
router.include_router(category.router, prefix="/blog/category", tags=["Category"])
router.include_router(email.router, prefix="/notifications", tags=["Notifications"])
router.include_router(comment_ws.router, prefix="/ws", tags=["Websockets"])
