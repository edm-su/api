import re
from datetime import datetime, timezone

from pydantic import BaseModel, Field, validator

from app.internal.entity.user import User


class BasePost(BaseModel):
    title: str
    annotation: str | None = Field(default=None)
    text: dict[str, int | list[dict[str, str | dict]] | str]
    slug: str
    published_at: datetime | None = Field(default=None)
    thumbnail: str | None = Field(default=None)

    @validator("slug")
    def slug_regexp(cls, v: str) -> str:  # noqa: N805, ANN101
        v = v.strip()
        if re.match("^[a-z0-9]+(?:-[a-z0-9]+)*$", v) is None:
            error = "может состоять только из латинских символов, чисел и -"
            raise ValueError(error)
        return v


class CreatePost(BasePost):
    @validator("published_at", always=True)
    def time_after_now(
        cls,  # noqa: ANN101, N805
        v: datetime,
    ) -> datetime:
        if v is None:
            return datetime.now(timezone.utc)
        if v < datetime.now(timezone.utc):
            error = "должно быть больше текущего"
            raise ValueError(error)
        return v


class NewPostDTO(CreatePost):
    user: User


class Post(BasePost):
    id: int
    user_id: int
