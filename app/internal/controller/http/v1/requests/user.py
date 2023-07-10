import re
from typing import Any

from pydantic import BaseModel, EmailStr, Field, SecretStr, validator


class SignUpRequest(BaseModel):
    username: str = Field(..., example="user", title="Username")
    email: EmailStr = Field(..., example="example@example.com", title="Email")
    password: SecretStr = Field(
        ...,
        example="password",
        title="Password",
        min_length=8,
    )

    @validator("username")
    def username_regexp(cls, v: str) -> str:  # noqa: ANN101, N805
        v = v.strip()
        if re.match(r"^[a-zA-Z0-9]+_?[a-zA-Z0-9]+$", v) is None:
            text_error = (
                "may contain Latin characters, numbers, "
                "or the underscore character.  "
                "Begin and end with a Latin symbol only"
            )
            raise ValueError(text_error)
        return v


class ActivateUserRequest(BaseModel):
    id: int = Field(..., example=1, title="User ID")
    activation_code: str = Field(
        ...,
        example="AAAAAAAAAA",
        title="Activation code",
        pattern=r"^[A-Z\d]{10}$",
    )


class SignInRequest(BaseModel):
    email: EmailStr = Field(..., example="example@example.com", title="Email")
    password: SecretStr = Field(
        ...,
        example="password",
        title="Password",
        min_length=8,
    )
    remember_me: bool = Field(
        default=False,
        example=False,
        title="Remember me",
        description="Issue a refresh token valid for 1 month",
    )


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., example="example@example.com", title="Email")


class ChangePasswordRequest(BaseModel):
    user_id: int = Field(..., example=1, title="User ID")
    old_password: SecretStr | None = Field(
        None,
        example="old_password",
        title="Old password",
        min_length=8,
    )
    new_password: SecretStr = Field(
        ...,
        example="new_password",
        title="New password",
        min_length=8,
    )
    reset_code: str | None = Field(
        None,
        example="reset_code",
        title="Reset code",
        pattern=r"^[A-Z\d]{10}$",
    )

    @validator("old_password")
    def old_password_must_be_present(
        cls,  # noqa: N805, ANN101
        v: SecretStr,
        values: dict[str, Any],
    ) -> SecretStr:
        if not v and not values.get("reset_code"):
            text_error = "must be present"
            raise ValueError(text_error)
        return v

    @validator("reset_code")
    def reset_code_or_old_password_must_be_present(
        cls,  # noqa: ANN101, N805
        v: SecretStr,
        values: dict[str, Any],
    ) -> SecretStr | None:
        if values.get("old_password") and v:
            return None
        return v
