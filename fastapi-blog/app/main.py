from fastapi import FastAPI
from app.api.v1 import router as api_v1_router
from app.db.init_db import init_db

app = FastAPI(title="FastAPI Blog")

app.include_router(api_v1_router, prefix="/api/v1")

@app.on_event("startup")
def on_startup():
    init_db()
