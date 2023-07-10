from datetime import date

from pydantic import (
    BaseModel,
    Field,
    FieldValidationInfo,
    field_validator,
)
from slugify import slugify

from app.internal.entity.common import AttributeModel


class Video(AttributeModel):
    id: int
    title: str
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    slug: str


class NewVideoDto(BaseModel):
    title: str
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    slug: str | None = Field(None)

    @field_validator("slug", mode="before")
    @classmethod
    def generate_slug(
        cls: type["NewVideoDto"],
        v: str,
        info: FieldValidationInfo,
    ) -> str:
        if not v:
            return slugify(info.data["title"])
        return v
