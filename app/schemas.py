from pydantic import BaseModel


class ChannelBase(BaseModel):
    name: str
    slug: str
    image: str


class Channel(ChannelBase):
    id: int

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    name: str
    slug: str
    image: str


class Event(EventBase):
    id: int

    class Config:
        orm_mode = True
