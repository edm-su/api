from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, validator
from slugify import slugify


class BaseLiveStream(BaseModel):
    title: str = Field(..., max_length=256, min_length=1)
    cancelled: bool
    start_time: datetime
    end_time: datetime = Field(None)
    image: str = Field(None)
    genres: list[str] = Field([])
    url: HttpUrl
    djs: list[str] = Field([])
    slug: str = Field(None)

    @validator('end_time')
    def end_time_after_start_time(cls, v: datetime, values: dict) -> datetime:
        if v and v < values['start_time']:
            raise ValueError('позже даты окончания')
        return v


class CreateLiveStream(BaseLiveStream):
    @validator('slug', always=True)
    def set_slug(cls, v: str, values: dict) -> str:
        return slugify(values['title'])


class LiveStream(BaseLiveStream):
    id: int
