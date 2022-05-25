from datetime import date

from pydantic import BaseModel, Field, validator
from slugify import slugify


class VideoBase(BaseModel):
    title: str
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    slug: str | None = Field(default=None)


class CreateVideo(VideoBase):
    slug: str = Field(None)

    @validator("slug", always=True)
    def generate_slug(cls, v: str, values: dict) -> str:  # noqa: N805, ANN101
        if not v:
            return slugify(values["title"])
        return v

    class Config:
        fields = {"id": {"exclude": True}}


class PgVideo(VideoBase):
    id: int
    liked: bool = Field(default=False)


class MeilisearchVideo(VideoBase):
    id: int

    class Config:
        json_encoders = {date: lambda d: int(d.strftime("%s"))}
