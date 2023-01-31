import re
from datetime import datetime

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    IPvAnyAddress,
    SecretStr,
    validator,
)


class UserBase(BaseModel):
    username: str

    @validator("username")
    def username_regexp(cls, v: str) -> str:
        v = v.strip()
        if re.match(r"^[a-zA-Z0-9]+_?[a-zA-Z0-9]+$", v) is None:
            raise ValueError(
                "может содержать латинские символы, цифры, "
                "или знак подчёркивания."
                " Начинаться и заканчиваться только латинским символом",
            )
        return v


class AdvancedUser(UserBase):
    email: EmailStr


class Admin(BaseModel):
    is_admin: bool


class MyUser(AdvancedUser, Admin):
    id: int


class User(BaseModel):
    id: int = Field(..., gt=0)
    username: str = Field(..., min_length=3)
    email: EmailStr = Field(...)
    hashed_password: SecretStr | None = Field(None, alias="password")
    is_active: bool = Field(False)
    is_admin: bool = Field(False)
    is_banned: bool = Field(False)
    created_at: datetime = Field(..., alias="created")
    last_login: datetime | None = Field(None)
    last_login_ip: IPvAnyAddress | None = Field(None)


class UserPassword(BaseModel):
    password: str

    @validator("password")
    def password_complexity(cls, v: str) -> str:
        min_length = 6
        if len(v) < 6:
            raise ValueError(f"минимальная длина пароля {min_length} символов")
        return v


class NewUserDto(AdvancedUser):
    id: int | None = Field(None, gt=0)
    password: SecretStr = Field(...)
    hashed_password: SecretStr | None = Field(None)
    activation_code: SecretStr | None = Field(None)
    is_active: bool = Field(False)


class ActivateUserDto(BaseModel):
    id: int
    activation_code: SecretStr


class ResetPasswordDto(BaseModel):
    id: int
    code: SecretStr
    expires: datetime


class ChangePasswordDto(BaseModel):
    id: int
    old_password: SecretStr
    hashed_old_password: SecretStr | None = Field(None)
    new_password: SecretStr
    hashed_new_password: SecretStr | None = Field(None)


class ChangePasswordByResetCodeDto(BaseModel):
    id: int
    code: SecretStr
    new_password: SecretStr
    hashed_new_password: SecretStr | None = Field(None)


class CreateUser(AdvancedUser, UserPassword):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
