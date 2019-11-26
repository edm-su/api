from fastapi import FastAPI

from app.routers import channels, events, djs, videos

app = FastAPI()

app.include_router(channels.router)
app.include_router(events.router)
app.include_router(djs.router)
app.include_router(videos.router)
