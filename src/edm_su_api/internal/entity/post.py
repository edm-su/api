from datetime import datetime, timezone
from typing import Any

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
    updated_at: datetime | None = Field(None, examples=[datetime.now(tz=timezone.utc)])
    updated_by: UUID4 | None = Field(None)


class PostEditHistory(BaseModel):
    """Model for edit history record"""

    id: int
    post_id: int
    edited_at: datetime
    description: str
    edited_by: UUID4


class UpdatePost(BaseModel):
    """Model for updating a post"""

    title: str | None = Field(None, min_length=1, max_length=100)
    annotation: str | None = Field(None, max_length=500)
    text: dict[str, Any] | None = None
    thumbnail: str | None = None
    published_at: datetime | None = None


class UpdatePostDTO(UpdatePost):
    """DTO for updating with additional data"""

    user: User
    save_history: bool = False
    history_description: str | None = None
