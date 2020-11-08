from pydantic import BaseModel, Field


class BaseChannel(BaseModel):
    name: str
    slug: str
    yt_id: str
    yt_thumbnail: str
    yt_banner: str = Field(None)


class Channel(BaseChannel):
    id: int
