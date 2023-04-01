from datetime import datetime

from pydantic import BaseModel, validator


class CommentBase(BaseModel):
    text: str

    @validator("text")
    def max_text_length(cls, v: str) -> str:  # noqa: N805, ANN101
        max_text_length = 120
        if len(v) > max_text_length:
            error = "превышает максимальную длину (120 символов)"
            raise ValueError(error)
        return v


class Comment(CommentBase):
    id: int
    user_id: int
    published_at: datetime
    video_id: int
