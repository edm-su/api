from datetime import date

from pydantic import BaseModel


class VideoBase(BaseModel):
    title: str
    slug: str
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    channel_id: int = None
    liked: bool = False


class Video(VideoBase):
    id: int
