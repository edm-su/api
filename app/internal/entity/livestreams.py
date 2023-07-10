from datetime import datetime

from pydantic import Field, HttpUrl

from app.internal.entity.common import AttributeModel, BaseModel


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


class LiveStream(BaseLiveStream, AttributeModel):
    id: int
