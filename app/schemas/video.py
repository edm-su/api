from datetime import date
from typing import List

from pydantic import BaseModel

from app.schemas.channel import Channel


class VideoBase(BaseModel):
    title: str
    slug: str
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    channel: Channel = None
    liked: bool = False


class Video(VideoBase):
    id: int

    class Config:
        orm_mode = True


class VideoList(BaseModel):
    total_count: int = 0
    videos: List[Video] = []
