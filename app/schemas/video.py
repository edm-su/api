from datetime import date

from pydantic import BaseModel, Field, validator
from slugify import slugify


class VideoBase(BaseModel):
    title: str
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    slug: str = Field(default=None)


class CreateVideo(VideoBase):
    @validator("slug", always=True)
    def generate_slug(cls, v: str, values: dict) -> str:  # noqa: N805, ANN101
        if not v:
            return slugify(values["title"])
        return v

    class Config:
        fields = {"id": {"exclude": True}}


class DbVideo(VideoBase):
    id: int


class PgVideo(DbVideo):
    pass


class MeilisearchVideo(DbVideo):
    class Config:
        json_encoders = {date: lambda d: int(d.strftime("%s"))}
