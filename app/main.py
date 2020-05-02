from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.db import database
from app.routers import channels, videos, users, comments, posts, images

app = FastAPI()


@app.on_event('startup')
async def startup():
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()


origins = [
    "http://edm.su",
    "https://edm.su",
    "http://localhost:3000",
    "http://edm.local"
]

app.include_router(channels.router)
app.include_router(videos.router)
app.include_router(users.router)
app.include_router(comments.router)
app.include_router(posts.router)
app.include_router(images.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
