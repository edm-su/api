import re

from datetime import date
from typing import List

from pydantic import BaseModel, EmailStr, validator


class ChannelBase(BaseModel):
    name: str
    slug: str
    yt_id: str
    yt_thumbnail: str
    yt_banner: str = None


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


class DjBase(BaseModel):
    name: str
    slug: str
    image: str


class Dj(DjBase):
    id: int

    class Config:
        orm_mode = True


class VideoBase(BaseModel):
    title: str
    slug: str
    date: date
    yt_id: str
    yt_thumbnail: str
    duration: int
    event: Event = None
    channel: Channel = None
    djs: List[Dj] = []


class Video(VideoBase):
    id: int

    class Config:
        orm_mode = True


class VideoList(BaseModel):
    total_count: int = 0
    videos: List[Video] = []


class UserBase(BaseModel):
    nickname: str
    email: EmailStr

    @validator('nickname')
    def nickname_regexp(cls, v):
        v = v.strip()
        if re.match('^[A-Za-z0-9а-яА-Я]+([A-Za-z0-9а-яА-Я]*|[._\s-]?[A-Za-z0-9а-яА-Я]+)*$', v) is None:
            raise ValueError('может содержать английские и русские буквы, цифры, пробел, точку или знак подчёркивания.'
                             ' Начинаться и заканчиваться только буквой или цифрой')
        return v


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class CreateUser(UserBase):
    password: str
    password_confirm: str

    @validator('password')
    def password_complexity(cls, v):
        min_len = 6
        if len(v) < 6:
            raise ValueError(f'минимальная длинна пароля {min_len} символов')
        return v

    @validator('password_confirm')
    def password_confirmation(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('пароли не совпадают')
        return v
