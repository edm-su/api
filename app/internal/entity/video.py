from datetime import date
from pydantic import (
    BaseModel,
    Field,
    validator,
)
from slugify import slugify


class Video(BaseModel):
    id: int
    title: str
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    slug: str = Field(None)


class NewVideoDto(BaseModel):
    title: str
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    slug: str = Field(None)

    @validator(
        "slug",
        always=True,
    )
    def generate_slug(
        cls,
        v: str,
        values: dict,
    ) -> str:
        if not v:
            v = slugify(values["title"])
        return v
