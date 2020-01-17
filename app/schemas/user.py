import re

from pydantic import BaseModel, validator, EmailStr


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
