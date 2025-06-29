from datetime import date

from pydantic import (
    BaseModel,
    Field,
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
    is_favorite: bool = Field(default=False)
    is_blocked_in_russia: bool = Field(default=False)


class NewVideoDto(SlugMixin, BaseModel):
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    is_blocked_in_russia: bool = Field(default=False)


class UpdateVideoDto(SlugMixin, BaseModel):
    date: date
    is_blocked_in_russia: bool = Field(default=False)
