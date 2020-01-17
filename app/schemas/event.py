from pydantic import BaseModel


class EventBase(BaseModel):
    name: str
    slug: str
    image: str


class Event(EventBase):
    id: int

    class Config:
        orm_mode = True
