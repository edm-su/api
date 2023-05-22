from datetime import datetime

from pydantic import BaseModel, Field

from app.internal.entity.video import Video
from app.internal.usecase.user import User


class CommentBase(BaseModel):
    text: str = Field(max_text_length=120)


class NewCommentDto(CommentBase):
    user: User
    video: Video


class Comment(CommentBase):
    id: int
    user_id: int
    published_at: datetime
    video_id: int

    class Config:
        orm_mode = True
