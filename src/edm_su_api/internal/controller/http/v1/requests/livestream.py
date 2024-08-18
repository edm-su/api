from datetime import datetime, timezone

from pydantic import (
    Field,
    HttpUrl,
    ValidationInfo,
    field_validator,
)
from slugify import slugify

from edm_su_api.internal.entity.common import BaseModel


class CreateLiveStreamRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=256,
        examples=["Live stream title"],
    )
    cancelled: bool = Field(default=False, title="Cancelled")
    start_time: datetime = Field(
        ...,
        examples=[datetime.now(tz=timezone.utc)],
    )
    end_time: datetime = Field(
        ...,
        examples=[datetime.now(tz=timezone.utc)],
    )
    image: str = Field(
        ...,
        examples=["https://example.com/image.png"],
    )
    genres: list[str | None] = Field(
        [],
        examples=["genre1", "genre2"],
    )
    url: HttpUrl = Field(
        ...,
        examples=["https://example.com"],
    )
    slug: str | None = Field(
        None,
        examples=["live-stream-slug"],
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )

    @field_validator("end_time")
    @classmethod
    def end_time_after_start_time(
        cls: type["CreateLiveStreamRequest"],
        v: datetime,
        info: ValidationInfo,
    ) -> datetime:
        if v < info.data["start_time"]:
            error_text = "Must be after the start date"
            raise ValueError(error_text)
        return v

    @field_validator("slug", mode="before")
    @classmethod
    def set_slug(
        cls: type["CreateLiveStreamRequest"],
        v: str,
        info: ValidationInfo,
    ) -> str:
        if not v:
            return slugify(info.data["title"])
        return v
