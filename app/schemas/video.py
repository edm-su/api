from datetime import date

from pydantic import BaseModel, Field, validator
from slugify import slugify


class VideoBase(BaseModel):
    title: str
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    liked: bool = Field(default=False)


class CreateVideo(VideoBase):
    slug: str = Field(None)

    @validator("slug", always=True)
    def generate_slug(cls, v: str, values: dict) -> str:  # noqa: N805, ANN101
        if not v:
            v = slugify(values["title"])
        return v  # noqa: RET504


class Video(VideoBase):
    id: int
    slug: str = Field(None)


class MeilisearchVideo(BaseModel):
    id: int
    title: str
    date: date
    slug: str
    yt_thumbnail: str
    duration: int

    class Config:
        json_encoders = {date: lambda d: int(d.strftime("%s"))}
