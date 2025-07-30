from fastapi import FastAPI
from app.api.v1 import user, post, comment, media
from app.db.init_db import init_db

app = FastAPI(title="FastAPI Blog")

app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(post.router, prefix="/api/v1/blog", tags=["Blogs"])
app.include_router(comment.router, prefix="/api/v1/blog/comments", tags=["Comments"])
app.include_router(media.router, prefix="/api/v1/blog/media", tags=["Media"])

@app.on_event("startup")
def on_startup():
    init_db()
