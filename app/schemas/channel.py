from pydantic import BaseModel


class ChannelBase(BaseModel):
    name: str
    slug: str
    yt_id: str
    yt_thumbnail: str
    yt_banner: str = None


class Channel(ChannelBase):
    id: int

    class Config:
        orm_mode = True
