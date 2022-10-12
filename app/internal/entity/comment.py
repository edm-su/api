from datetime import datetime

from pydantic import BaseModel, validator

from app.internal.entity.video import Video


class NewCommentDto(BaseModel):
    text: str
    user_id: int
    video: Video

    @validator("text")
    def max_text_length(cls, v: str) -> str:
        if len(v) > 120:
            raise ValueError("превышает максимальную длину (120 символов)")
        return v


class CommentBase(BaseModel):
    text: str

    @validator("text")
    def max_text_length(cls, v: str) -> str:
        if len(v) > 120:
            raise ValueError("превышает максимальную длину (120 символов)")
        return v


class Comment(CommentBase):
    id: int
    user_id: int
    published_at: datetime
    video_id: int
