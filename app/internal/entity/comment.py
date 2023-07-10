from datetime import datetime

from pydantic import Field

from app.internal.entity.common import AttributeModel, BaseModel
from app.internal.entity.video import Video
from app.internal.usecase.user import User


class CommentBase(BaseModel):
    text: str = Field(max_length=120)


class NewCommentDto(CommentBase):
    user: User
    video: Video


class Comment(AttributeModel, CommentBase):
    id: int
    user_id: int
    published_at: datetime
    video_id: int
