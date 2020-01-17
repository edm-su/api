from datetime import datetime

from pydantic import BaseModel


class CommentBase(BaseModel):
    text: str
    video_id: int


class Comment(CommentBase):
    id: int
    user_id: int
    published_at: datetime

    class Config:
        orm_mode = True
