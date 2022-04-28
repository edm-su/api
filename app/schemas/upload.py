from pydantic import BaseModel, HttpUrl


class ImageURLDTO(BaseModel):
    url: HttpUrl
