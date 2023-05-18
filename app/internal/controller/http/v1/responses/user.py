from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, IPvAnyAddress, SecretStr


class SignUpResponse(BaseModel):
    id: int = Field(..., example=1, title="User ID")
    username: str = Field(..., example="user", title="Username")
    email: str = Field(..., example="example@example.com", title="Email")
    is_active: bool = Field(
        default=False,
        example=False,
        title="Whether the user is activated",
    )


class MeResponse(BaseModel):
    id: int = Field(..., example=1, title="User ID")
    username: str = Field(..., example="user", title="Username")
    email: EmailStr = Field(..., example="example@example.com", title="Email")
    is_active: bool = Field(
        default=False,
        example=False,
        title="Whether the user is activated",
    )
    is_admin: bool = Field(
        default=False,
        example=False,
        title="Whether the user is an administrator",
    )
    is_banned: bool = Field(
        default=False,
        example=False,
        title="Whether the user is banned",
    )
    created_at: datetime = Field(
        ...,
        example="2021-01-01T00:00:00+00:00",
        title="Creation time",
    )
    last_login: datetime | None = Field(
        ...,
        example="2021-01-01T00:00:00+00:00",
        title="Last login time",
    )
    last_login_ip: IPvAnyAddress | None = Field(
        ...,
        example="127.0.0.1",
        title="Last login IP",
    )


class SignInResponse(BaseModel):
    access_token: SecretStr = Field(
        ...,
        example="access_token",
        title="Access token",
    )
    token_type: str = Field(
        default="Bearer",
        title="Token type",
    )
    refresh_token: SecretStr | None = Field(
        default=None,
        example="refresh_token",
        title="Refresh token",
        description="refresh token valid for 1 month",
    )
