from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as api_v1_router
from app.db.init_db import init_db
from app.middleware.view_counter import ViewCountMiddleware

app = FastAPI(title="FastAPI Blog")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(ViewCountMiddleware)

app.include_router(api_v1_router, prefix="/api/v1")

@app.on_event("startup")
def on_startup():
    init_db()
