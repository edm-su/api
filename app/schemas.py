import re

from datetime import date, datetime
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
    username: str

    @validator('username')
    def username_regexp(cls, v):
        v = v.strip()
        if re.match('^[A-Za-z0-9а-яА-Я]+([A-Za-z0-9а-яА-Я]*|[._\s-]?[A-Za-z0-9а-яА-Я]+)*$', v) is None:
            raise ValueError('может содержать английские и русские буквы, цифры, пробел, точку или знак подчёркивания.'
                             ' Начинаться и заканчиваться только буквой или цифрой')
        return v


class AdvancedUser(UserBase):
    email: EmailStr


class Admin(BaseModel):
    is_admin: bool


class MyUser(AdvancedUser, Admin):
    id: int

    class Config:
        orm_mode = True


class User(UserBase, Admin):
    id: int

    class Config:
        orm_mode = True


class UserRecovery(BaseModel):
    email: EmailStr


class UserPassword(BaseModel):
    password: str
    password_confirm: str

    @validator('password')
    def password_complexity(cls, v):
        min_len = 6
        if len(v) < 6:
            raise ValueError(f'минимальная длина пароля {min_len} символов')
        return v

    @validator('password_confirm')
    def password_confirmation(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('пароли не совпадают')
        return v


class CreateUser(AdvancedUser, UserPassword):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class ChangePassword(UserPassword):
    old_password: str


class CommentBase(BaseModel):
    text: str
    video_id: int


class Comment(CommentBase):
    id: int
    user_id: int
    published_at: datetime

    class Config:
        orm_mode = True
