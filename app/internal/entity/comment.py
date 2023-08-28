from datetime import datetime

from pydantic import UUID4, Field

from app.internal.entity.common import AttributeModel, BaseModel
from app.internal.entity.user import User
from app.internal.entity.video import Video


class CommentBase(BaseModel):
    text: str = Field(max_length=120)


class NewCommentDto(CommentBase):
    user: User
    video: Video


class Comment(AttributeModel, CommentBase):
    id: int
    user_id: UUID4
    published_at: datetime
    video_id: int
