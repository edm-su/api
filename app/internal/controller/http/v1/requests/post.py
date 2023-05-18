from datetime import datetime

from pydantic import BaseModel, Field, validator


class CreatePostRequest(BaseModel):
    title: str = Field(
        ...,
        example="Post title",
        title="Post title",
        min_length=1,
        max_length=100,
    )
    annotation: str | None = Field(
        default=None,
        example="Post annotation",
        min_length=1,
        max_length=500,
    )
    text: dict[str, int | list[dict[str, str | dict]] | str]
    slug: str = Field(
        ...,
        example="post-slug",
        title="Post slug",
        regex=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    published_at: datetime | None = Field(
        default=None,
        example=datetime.now(),
        title="Post published at",
    )
    thumbnail: str | None = Field(
        default=None,
        example="https://example.com/image.png",
        title="Post thumbnail",
    )

    @validator("published_at")
    def time_after_now(
        cls,  # noqa: ANN101, N805
        v: datetime | None,
    ) -> datetime:
        if v is None:
            return datetime.utcnow()
        if v < datetime.utcnow():
            error = "Must be larger than the current"
            raise ValueError(error)
        return v
