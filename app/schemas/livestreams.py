from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, validator
from slugify import slugify


class BaseLiveStream(BaseModel):
    title: str = Field(..., max_length=256, min_length=1)
    cancelled: bool = Field(default=False)
    start_time: datetime
    end_time: datetime = Field(None)
    image: str = Field(None)
    genres: list[str] = Field([])
    url: HttpUrl
    djs: list[str] = Field([])
    slug: str = Field(None)

    @validator("end_time")
    def end_time_after_start_time(
        cls,  # noqa: N805, ANN101
        v: datetime,
        values: dict,
    ) -> datetime:
        if v and v < values["start_time"]:
            error = "позже даты окончания"
            raise ValueError(error)
        return v


class CreateLiveStream(BaseLiveStream):
    @validator("slug", always=True)
    def set_slug(
        cls,  # noqa: ANN101, N805
        v: str,  # noqa: ARG002
        values: dict,
    ) -> str:
        return slugify(values["title"])


class LiveStream(BaseLiveStream):
    id: int
