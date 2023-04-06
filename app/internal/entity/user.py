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
    def username_regexp(cls, v: str) -> str:  # noqa: N805, ANN101
        v = v.strip()
        if re.match(r"^[a-zA-Z0-9]+_?[a-zA-Z0-9]+$", v) is None:
            error_text = (
                "может содержать латинские символы, цифры, "
                "или знак подчёркивания."
                " Начинаться и заканчиваться только латинским символом"
            )
            raise ValueError(error_text)
        return v


class AdvancedUser(UserBase):
    email: EmailStr


class SignInDto(BaseModel):
    email: EmailStr
    password: SecretStr
    hashed_password: SecretStr | None = Field(default=None)


class Admin(BaseModel):
    is_admin: bool


class MyUser(AdvancedUser, Admin):
    id: int


class User(BaseModel):
    id: int = Field(..., gt=0)
    username: str = Field(..., min_length=3)
    email: EmailStr = Field(...)
    hashed_password: SecretStr | None = Field(default=None, alias="password")
    activation_code: SecretStr | None = Field(default=None)
    is_active: bool = Field(default=False)
    is_admin: bool = Field(default=False)
    is_banned: bool = Field(default=False)
    created_at: datetime = Field(..., alias="created")
    last_login: datetime | None = Field(default=None)
    last_login_ip: IPvAnyAddress | None = Field(default=None)


class UserPassword(BaseModel):
    password: str

    @validator("password")
    def password_complexity(cls, v: str) -> str:  # noqa: ANN101, N805
        min_length = 6
        if len(v) < min_length:
            error_text = f"минимальная длина пароля {min_length} символов"
            raise ValueError(error_text)
        return v


class NewUserDto(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr = Field(...)
    password: SecretStr = Field(...)
    hashed_password: SecretStr | None = Field(default=None)
    activation_code: SecretStr | None = Field(default=None)
    is_active: bool = Field(default=False)

    @validator("username")
    def username_regexp(cls, v: str) -> str:  # noqa: N805, ANN101
        v = v.strip()
        if re.match(r"^[a-zA-Z0-9]+_?[a-zA-Z0-9]+$", v) is None:
            error_text = (
                "может содержать латинские символы, цифры, "
                "или знак подчёркивания."
                " Начинаться и заканчиваться только латинским символом",
            )
            raise ValueError(error_text)
        return v


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
    hashed_old_password: SecretStr | None = Field(default=None)
    new_password: SecretStr
    hashed_new_password: SecretStr | None = Field(default=None)


class ChangePasswordByResetCodeDto(BaseModel):
    id: int
    code: SecretStr
    new_password: SecretStr
    hashed_new_password: SecretStr | None = Field(default=None)


class CreateUser(AdvancedUser, UserPassword):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_admin: bool = Field(default=False)
