from pydantic import BaseModel, Field, HttpUrl


class ImageURLs(BaseModel):
    jpeg: HttpUrl | None = Field(None)


class ImageURL(BaseModel):
    url: HttpUrl
