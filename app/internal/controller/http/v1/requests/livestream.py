from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, validator
from slugify import slugify


class CreateLiveStreamRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=256,
        title="Title",
        example="Live stream title",
    )
    cancelled: bool = Field(default=False, title="Cancelled")
    start_time: datetime = Field(
        ...,
        title="Start time",
        example=datetime.now(),
    )
    end_time: datetime = Field(
        ...,
        title="End time",
        example=datetime.now(),
    )
    image: str = Field(
        ...,
        title="Image",
        example="https://example.com/image.png",
    )
    genres: list[str | None] = Field(
        [],
        title="Genres",
        example=["genre1", "genre2"],
    )
    url: HttpUrl = Field(
        ...,
        title="URL",
        example="https://example.com",
    )
    slug: str = Field(  # type: ignore[assignment]
        None,
        title="Slug",
        example="live-stream-slug",
    )

    @validator("end_time")
    def end_time_after_start_time(
        cls,  # noqa: N805, ANN101
        v: datetime,
        values: dict[str, Any],
    ) -> datetime:
        if v and v < values["start_time"]:
            error_text = "Must be after the start date"
            raise ValueError(error_text)
        return v

    @validator("slug", always=True)
    def set_slug(
        cls,  # noqa: ANN101, N805
        v: str,
        values: dict,
    ) -> str:
        if not v:
            return slugify(values["title"])
        return v
