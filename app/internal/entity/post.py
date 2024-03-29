from datetime import datetime

from pydantic import UUID4, Field

from app.internal.entity.common import AttributeModel, BaseModel
from app.internal.entity.user import User


class BasePost(BaseModel):
    title: str
    annotation: str | None = Field(default=None)
    text: dict[str, int | list[dict[str, str | dict]] | str]
    slug: str
    published_at: datetime = Field(...)
    thumbnail: str | None = Field(default=None)


class NewPostDTO(BasePost):
    user: User


class Post(BasePost, AttributeModel):
    id: int
    user_id: UUID4
