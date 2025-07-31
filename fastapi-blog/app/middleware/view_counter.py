from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.orm import Session
from app.models import Post
from app.db.session import SessionLocal

import re

class ViewCountMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        match = re.match(r"^/api/v1/blog/post/(\d+)$", path)
        if match and method == "GET":
            post_id = int(match.group(1))
            # Tạo session DB để cập nhật
            db: Session = SessionLocal()
            post = db.query(Post).filter(Post.id == post_id).first()
            if post:
                post.views += 1
                db.commit()
            db.close()

        response: Response = await call_next(request)
        return response
