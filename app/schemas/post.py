import re
from datetime import datetime, timezone

from pydantic import BaseModel, validator


class BasePost(BaseModel):
    title: str
    annotation: str
    text: str
    slug: str
    published_at: datetime
    thumbnail: str = None

    @validator('slug')
    def slug_regexp(cls, v):
        v = v.strip()
        if re.match('^[a-z0-9]+(?:-[a-z0-9]+)*$', v) is None:
            raise ValueError('может состоять только из латинских символов, чисел и -')
        return v


class CreatePost(BasePost):
    @validator('published_at')
    def time_after_now(cls, v):
        if v < datetime.now(timezone.utc):
            raise ValueError('должно быть больше текущего')
        return v


class Post(BasePost):
    id: int
    user_id: int
