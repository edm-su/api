from datetime import date
from typing import List

from pydantic import BaseModel


class ChannelBase(BaseModel):
    name: str
    slug: str
    youtube_id: str
    thumbnail_url: str


class Channel(ChannelBase):
    id: int

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    name: str
    slug: str
    image: str


class Event(EventBase):
    id: int

    class Config:
        orm_mode = True


class DjBase(BaseModel):
    name: str
    slug: str
    image: str


class Dj(DjBase):
    id: int

    class Config:
        orm_mode = True


class VideoBase(BaseModel):
    title: str
    slug: str
    date: date
    yt_id: str
    yt_thumbnail: str
    event: Event = None
    channel: Channel = None
    djs: List[Dj] = []


class Video(VideoBase):
    id: int

    class Config:
        orm_mode = True


class VideoList(BaseModel):
    total_count: int = 0
    videos: List[Video] = []
