from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import jwt
from argon2 import PasswordHasher
from pydantic import EmailStr, Field, IPvAnyAddress, SecretStr, computed_field
from typing_extensions import Self

from app.internal.entity.common import AttributeModel, BaseModel
from app.internal.entity.settings import settings


class UserBase(BaseModel):
    username: str


class AdvancedUser(UserBase):
    email: EmailStr


class SignInDto(BaseModel):
    email: EmailStr
    password: SecretStr


class Admin(BaseModel):
    is_admin: bool


class MyUser(AdvancedUser, Admin):
    id: int


class User(AttributeModel):
    id: int = Field(..., gt=0)
    username: str = Field(..., min_length=3)
    email: EmailStr = Field(...)
    hashed_password: SecretStr = Field(..., alias="password")
    activation_code: SecretStr | None = Field(default=None)
    is_active: bool = Field(default=False)
    is_admin: bool = Field(default=False)
    is_banned: bool = Field(default=False)
    created_at: datetime = Field(..., alias="created")
    last_login: datetime | None = Field(default=None)
    last_login_ip: IPvAnyAddress | None = Field(default=None)


class NewUserDto(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: SecretStr
    activation_code: SecretStr | None = Field(default=None)
    is_active: bool = Field(default=False)

    @computed_field  # type: ignore[misc]
    @property
    def hashed_password(self: Self) -> SecretStr:
        return SecretStr(get_password_hash(self.password.get_secret_value()))


class ActivateUserDto(BaseModel):
    id: int
    activation_code: str


class ResetPasswordDto(BaseModel):
    id: int
    code: SecretStr
    expires: datetime


class ChangePassword(BaseModel, ABC):
    new_password: SecretStr = Field(
        ...,
        examples=["new_password"],
        min_length=8,
    )

    @computed_field  # type: ignore[misc]
    @property
    def hashed_password(self: Self) -> SecretStr:
        return SecretStr(
            get_password_hash(self.new_password.get_secret_value()),
        )


class ChangePasswordBaseDto(ChangePassword, ABC):
    user_id: int = Field(..., examples=[1])


class OldPassword(BaseModel, ABC):
    old_password: SecretStr = Field(
        ...,
        examples=["old_password"],
        min_length=8,
    )


class ChangePasswordDto(ChangePasswordBaseDto, OldPassword):
    pass


class ChangePasswordByResetCodeDto(ChangePasswordBaseDto):
    code: SecretStr = Field(
        ...,
        examples=["AAAAAAAAAA"],
        min_length=10,
        max_length=10,
    )


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: int
    email: EmailStr
    username: str
    is_admin: bool = Field(default=False)
    token_id: int | None = Field(default=None)
    scope: list[str] = Field(default=[])

    def get_jwt_token(self: Self) -> str:
        to_encode = self.model_dump()
        return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


class AccessTokenData(TokenData):
    exp: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(minutes=30),
    )


class RefreshTokenData(TokenData):
    exp: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(days=30),
    )


class ApiTokenData(TokenData):
    exp: datetime | None = Field(default=None)


class TokenDataCreator(ABC):
    @abstractmethod
    def factory(self: Self, token_data: TokenData) -> TokenData:
        pass


class AccessTokenDataCreator(TokenDataCreator):
    def factory(self: Self, token_data: TokenData) -> AccessTokenData:
        return AccessTokenData(**token_data.model_dump())


class RefreshTokenDataCreator(TokenDataCreator):
    def factory(self: Self, token_data: TokenData) -> RefreshTokenData:
        refresh_token = RefreshTokenData(**token_data.model_dump())
        refresh_token.scope.append("user:refresh")
        return refresh_token


class ApiTokenDataCreator(TokenDataCreator):
    def factory(self: Self, token_data: TokenData) -> ApiTokenData:
        return ApiTokenData(**token_data.model_dump())


class UserTokenDTO(BaseModel):
    name: str
    expired_at: datetime | None = Field(default=None)


class UserToken(AttributeModel, UserTokenDTO):
    id: int
    created_at: datetime


def get_password_hash(password: str) -> str:
    ph = PasswordHasher()
    return ph.hash(password)
