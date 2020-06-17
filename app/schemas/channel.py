from pydantic import BaseModel


class BaseChannel(BaseModel):
    name: str
    slug: str
    yt_id: str
    yt_thumbnail: str
    yt_banner: str = None


class Channel(BaseChannel):
    id: int
