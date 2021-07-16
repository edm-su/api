from datetime import date

from pydantic import BaseModel, Field, validator
from slugify import slugify


class VideoBase(BaseModel):
    title: str
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    channel_id: int = Field(None)
    liked: bool = Field(False)


class CreateVideo(VideoBase):
    slug: str = Field(None)

    @validator('slug', always=True)
    def generate_slug(cls, v: str, values: dict) -> str:
        if not v:
            v = slugify(values['title'])
        return v


class Video(VideoBase):
    id: int
    slug: str = Field(None)
