from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers import channels, events, djs, videos, users, comments

app = FastAPI()

origins = [
    "http://edm.su",
    "https://edm.su",
    "http://localhost:3000"
]

app.include_router(channels.router)
app.include_router(events.router)
app.include_router(djs.router)
app.include_router(videos.router)
app.include_router(users.router)
app.include_router(comments.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
