from datetime import date
from typing import Annotated
from uuid import uuid4

from pydantic import (
    BaseModel,
    Field,
    ValidationInfo,
    field_validator,
)
from slugify import slugify
from typing_extensions import Self

from edm_su_api.internal.entity.common import AttributeModel


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
    slug: Annotated[str | None, Field(validate_default=True)] = None

    @field_validator("slug", mode="after")
    @classmethod
    def generate_slug(
        cls: type["NewVideoDto"],
        v: str | None,
        info: ValidationInfo,
    ) -> str:
        if not v:
            return slugify(info.data["title"])
        return v

    def expand_slug(self: Self) -> None:
        expansion = uuid4().hex[:8]
        self.slug = f"{expansion}-{self.slug}"
