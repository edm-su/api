from datetime import datetime, timezone

from pydantic import Field, field_validator

from app.internal.entity.common import BaseModel


class CreatePostRequest(BaseModel):
    title: str = Field(
        ...,
        examples=["Post title"],
        min_length=1,
        max_length=100,
    )
    annotation: str | None = Field(
        default=None,
        examples=["Annotation"],
        min_length=1,
        max_length=500,
    )
    text: dict[str, int | list[dict[str, str | dict]] | str]
    slug: str = Field(
        ...,
        examples=["post-slug"],
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    published_at: datetime = Field(
        examples=[datetime.utcnow()],
        default_factory=lambda: datetime.utcnow(),
    )
    thumbnail: str | None = Field(
        default=None,
        examples=["https://example.com/image.png"],
    )

    @field_validator("published_at", mode="after")
    @classmethod
    def time_after_now(
        cls: type["CreatePostRequest"],
        v: datetime,
    ) -> datetime:
        if v < datetime.now(tz=timezone.utc):
            error = "Must be larger than the current"
            raise ValueError(error)
        return v.replace(tzinfo=None)
