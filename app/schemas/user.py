import re

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    username: str

    @validator("username")
    def username_regexp(cls, v: str) -> str:  # noqa: N805, ANN101
        v = v.strip()
        if re.match(r"^[a-zA-Z0-9]+_?[a-zA-Z0-9]+$", v) is None:
            error = (
                "может содержать латинские символы, цифры, "
                "или знак подчёркивания."
                " Начинаться и заканчиваться только латинским символом"
            )
            raise ValueError(error)
        return v


class AdvancedUser(UserBase):
    email: EmailStr


class Admin(BaseModel):
    is_admin: bool


class MyUser(AdvancedUser, Admin):
    id: int


class User(UserBase, Admin):
    id: int


class UserPassword(BaseModel):
    password: str

    @validator("password")
    def password_complexity(cls, v: str) -> str:  # noqa: ANN101, N805
        min_length = 6

        if len(v) < min_length:
            error = f"минимальная длина пароля {min_length} символов"
            raise ValueError(error)
        return v


class NewUserDto(AdvancedUser):
    hashed_password: str = Field(..., alias="password")


class CreateUser(AdvancedUser, UserPassword):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
