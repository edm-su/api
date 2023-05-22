from datetime import date

from pydantic import BaseModel, Field, validator
from slugify import slugify


class Video(BaseModel):
    id: int
    title: str
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    slug: str = Field(...)

    class Config:
        orm_mode = True


class NewVideoDto(BaseModel):
    title: str
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    slug: str | None = Field(None)

    @validator(
        "slug",
        always=True,
    )
    def generate_slug(
        cls,  # noqa: N805, ANN101
        v: str,
        values: dict,
    ) -> str:
        if not v:
            return slugify(values["title"])
        return v
