from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.internal.entity.video import Video
from app.internal.usecase.user import User


class CommentBase(BaseModel):
    text: str = Field(max_length=120)


class NewCommentDto(CommentBase):
    user: User
    video: Video


class Comment(CommentBase):
    id: int
    user_id: int
    published_at: datetime
    video_id: int

    model_config = ConfigDict(from_attributes=True)
