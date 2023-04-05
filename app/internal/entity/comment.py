from datetime import datetime

from pydantic import BaseModel, validator

from app.internal.entity.video import Video
from app.internal.usecase.user import User


class CommentBase(BaseModel):
    text: str

    @validator("text")
    def max_text_length(cls, v: str) -> str:  # noqa: N805, ANN101
        max_text_length = 120
        if len(v) > max_text_length:
            error_text = (
                f"превышает максимальную длину ({max_text_length} символов)"
            )
            raise ValueError(error_text)
        return v

class NewCommentDto(CommentBase):
    user: User
    video: Video


class Comment(CommentBase):
    id: int
    user_id: int
    published_at: datetime
    video_id: int
