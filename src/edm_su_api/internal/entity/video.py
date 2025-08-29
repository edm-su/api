from datetime import date
from enum import Enum

from pydantic import (
    BaseModel,
    Field,
)

from edm_su_api.internal.entity.common import AttributeModel, SlugMixin


class DeleteType(Enum):
    PERMANENT = "permanent"
    TEMPORARY = "temporary"


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
    deleted: bool = Field(default=False)
    delete_type: DeleteType | None = Field(default=None)


class NewVideoDto(SlugMixin, BaseModel):
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    is_blocked_in_russia: bool = Field(default=False)


class UpdateVideoDto(SlugMixin, BaseModel):
    date: date
    is_blocked_in_russia: bool = Field(default=False)


class RestoreVideoDto(BaseModel):
    delete_type: DeleteType | None = Field(default=None)
