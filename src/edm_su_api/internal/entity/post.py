from datetime import datetime, timezone

from pydantic import UUID4, Field, FutureDatetime

from edm_su_api.internal.entity.common import AttributeModel, BaseModel
from edm_su_api.internal.entity.user import User


class BasePost(BaseModel):
    title: str = Field(
        ...,
        examples=["Post title"],
        min_length=1,
        max_length=100,
    )
    annotation: str | None = Field(
        default=None,
        examples=["Annotation"],
        max_length=500,
    )
    text: dict[str, int | list[dict[str, str | dict]] | str]
    slug: str = Field(
        ...,
        examples=["post-slug"],
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    published_at: datetime = Field(
        examples=[datetime.now(tz=timezone.utc)],
        default_factory=lambda: datetime.now(tz=timezone.utc),
    )
    thumbnail: str | None = Field(
        default=None,
        examples=["https://example.com/image.png"],
    )


class NewPost(BasePost):
    published_at: FutureDatetime = Field(
        examples=[datetime.now(tz=timezone.utc)],
        default_factory=lambda: datetime.now(tz=timezone.utc),
    )


class NewPostDTO(BasePost):
    user: User


class Post(BasePost, AttributeModel):
    id: int = Field(..., examples=[12345])
    user_id: UUID4 = Field(
        ...,
        examples=["c73caa8b-35fb-4c82-9ea4-a9500bcd2259"],
    )
