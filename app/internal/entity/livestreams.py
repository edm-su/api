from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class BaseLiveStream(BaseModel):
    title: str = Field(..., max_length=256, min_length=1)
    cancelled: bool = Field(default=False)
    start_time: datetime
    end_time: datetime = Field(...)
    image: str = Field(...)
    genres: list[str | None] = Field([])
    url: HttpUrl
    slug: str = Field(...)


class CreateLiveStreamDTO(BaseLiveStream):
    pass


class LiveStream(BaseLiveStream):
    id: int

    class Config:
        orm_mode = True
