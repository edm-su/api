from datetime import datetime, timedelta

import jwt
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    IPvAnyAddress,
    SecretStr,
)
from typing_extensions import Self

from app.internal.entity.settings import settings


class UserBase(BaseModel):
    username: str


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

    model_config = ConfigDict(from_attributes=True)


class NewUserDto(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: SecretStr
    hashed_password: SecretStr | None = Field(default=None)
    activation_code: SecretStr | None = Field(default=None)
    is_active: bool = Field(default=False)


class ActivateUserDto(BaseModel):
    id: int
    activation_code: str


class ResetPasswordDto(BaseModel):
    id: int
    code: SecretStr
    expires: datetime


class ChangePasswordDto(BaseModel):
    id: int
    old_password: SecretStr
    new_password: SecretStr
    hashed_new_password: SecretStr | None = Field(default=None)


class ChangePasswordByResetCodeDto(BaseModel):
    id: int
    code: SecretStr
    new_password: SecretStr
    hashed_new_password: SecretStr | None = Field(default=None)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_admin: bool = Field(default=False)
    token_id: int | None = Field(default=None)

    def get_jwt_token(
        self: Self,
        expires_delta: timedelta = timedelta(days=31),
    ) -> str:
        to_encode = self.dict()
        to_encode.update({"exp": datetime.utcnow() + expires_delta})
        return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")

    def access_token(self: Self) -> str:
        return self.get_jwt_token(expires_delta=timedelta(minutes=30))

    def refresh_token(self: Self) -> str:
        return self.get_jwt_token(expires_delta=timedelta(days=30))


class UserTokenDTO(BaseModel):
    name: str
    expired_at: datetime | None = Field(default=None)


class UserToken(UserTokenDTO):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
