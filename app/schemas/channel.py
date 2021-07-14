from pydantic import BaseModel, Field, validator
from slugify import slugify


class BaseChannel(BaseModel):
    name: str
    yt_id: str
    yt_thumbnail: str
    yt_banner: str = Field(None)


class NewChannel(BaseChannel):
    slug: str = Field(None)

    @validator('slug', always=True)
    def generate_slug(cls, v: str, values: dict) -> str:
        if not v:
            v = slugify(values['name'])
        return v


class Channel(BaseChannel):
    id: int
    slug: str = Field(None)
