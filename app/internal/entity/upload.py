from pydantic import BaseModel, HttpUrl


class ImageURLs(BaseModel):
    __root__: dict[str, HttpUrl]


class ImageURL(BaseModel):
    url: HttpUrl
