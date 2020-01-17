from pydantic import BaseModel


class DjBase(BaseModel):
    name: str
    slug: str
    image: str


class Dj(DjBase):
    id: int

    class Config:
        orm_mode = True
