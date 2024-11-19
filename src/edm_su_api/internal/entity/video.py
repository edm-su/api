from datetime import date

from pydantic import (
    BaseModel,
)

from edm_su_api.internal.entity.common import AttributeModel, SlugMixin


class Video(AttributeModel):
    id: int
    title: str
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    slug: str


class NewVideoDto(SlugMixin, BaseModel):
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int


class UpdateVideoDto(SlugMixin, BaseModel):
    id: int
    date: date
