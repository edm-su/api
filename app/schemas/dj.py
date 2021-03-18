from datetime import date

from pydantic import BaseModel, Field, HttpUrl, validator
from slugify import slugify


class BaseDJ(BaseModel):
    name: str = Field(min_length=1, max_length=32)
    is_group: bool = Field(False)
    real_name: str = Field(None, max_length=128)
    aliases: list[str] = Field(None)
    country: str
    genres: list[str] = Field(None)
    image: str
    birth_date: date
    site: HttpUrl = Field(None)
    slug: str = Field(None)


class CreateDJ(BaseDJ):
    group_members: list[int] = Field([])

    @validator('slug', always=True)
    def generate_slug(cls, v: str, values: dict) -> str:
        if not v:
            v = slugify(values['name'])
        return v


class DJ(BaseDJ):
    id: int
    member_of_groups: list[str] = Field([])
    group_members: list[str] = Field([])
