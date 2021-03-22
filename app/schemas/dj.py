from datetime import date

from pydantic import BaseModel, Field, HttpUrl, validator
from slugify import slugify


class BaseDJ(BaseModel):
    name: str = Field(min_length=1, max_length=32)
    is_group: bool = Field(False)
    real_name: str = Field(None, max_length=128)
    aliases: list[str] = Field(None)
    country: str = Field(None)
    genres: list[str] = Field(None)
    image: str = Field(None)
    birth_date: date = Field(None)
    site: HttpUrl = Field(None)


class CreateDJ(BaseDJ):
    group_members: list[int] = Field([])
    slug: str = Field(None)

    @validator('slug', always=True)
    def generate_slug(cls, v: str, values: dict) -> str:
        if not v:
            v = slugify(values['name'])
        return v


class ChangeDJ(BaseDJ):
    name: str = Field(None, min_length=1, max_length=32)
    group_members: list[int] = Field([])


class DJ(BaseDJ):
    id: int
    slug: str = Field(None)
    member_of_groups: list[str] = Field([])
    group_members: list[str] = Field([])
