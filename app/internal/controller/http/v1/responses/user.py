from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, IPvAnyAddress


class SignUpResponse(BaseModel):
    id: int = Field(..., examples=[1])
    username: str = Field(..., examples=["user"])
    email: str = Field(..., examples=["example@example.com"])
    is_active: bool = Field(default=False, examples=[False])


class MeResponse(BaseModel):
    id: int = Field(..., examples=[1])
    username: str = Field(..., examples=["user"])
    email: EmailStr = Field(..., examples=["example@example.com"])
    is_active: bool = Field(default=False, examples=[False])
    is_admin: bool = Field(default=False, examples=[False])
    is_banned: bool = Field(default=False, examples=[False])
    created_at: datetime = Field(..., examples=[datetime.now()])
    last_login: datetime | None = Field(..., examples=[datetime.now()])
    last_login_ip: IPvAnyAddress | None = Field(..., examples=["127.0.0.1"])


class SignInResponse(BaseModel):
    access_token: str = Field(..., examples=["access_token"])
    token_type: str = Field(default="Bearer")
    refresh_token: str | None = Field(
        default=None,
        examples=["refresh_token"],
        description="refresh token valid for 1 month",
    )


class RefreshTokenResponse(SignInResponse):
    refresh_token: str = Field(
        ...,
        examples=["refresh_token"],
        description="refresh token valid for 1 month",
    )
