from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import async_session
from app.models import Post

import re

class ViewCountMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        match = re.match(r"^/api/v1/blog/post/(\d+)$", path)
        if match and method == "GET":
            post_id = int(match.group(1))

            async with async_session() as session:
                result = await session.execute(select(Post).filter(Post.id == post_id))
                post = result.scalar_one_or_none()
                if post:
                    post.views += 1
                    await session.commit()

        response: Response = await call_next(request)
        return response
