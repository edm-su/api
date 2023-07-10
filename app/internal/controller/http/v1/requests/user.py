import re

from pydantic import (
    EmailStr,
    Field,
    FieldValidationInfo,
    SecretStr,
    field_validator,
)

from app.internal.entity.common import BaseModel


class SignUpRequest(BaseModel):
    username: str = Field(..., examples=["user"])
    email: EmailStr = Field(..., examples=["example@example.com"])
    password: SecretStr = Field(..., examples=["password"], min_length=8)

    @field_validator("username")
    @classmethod
    def username_regexp(cls: type["SignUpRequest"], v: str) -> str:
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
    id: int = Field(..., examples=[1])
    activation_code: str = Field(
        ...,
        examples=["AAAAAAAAAA"],
        pattern=r"^[A-Z\d]{10}$",
    )


class SignInRequest(BaseModel):
    email: EmailStr = Field(..., examples=["example@example.com"])
    password: SecretStr = Field(..., examples=["password"], min_length=8)
    remember_me: bool = Field(
        default=False,
        examples=[False],
        description="Issue a refresh token valid for 1 month",
    )


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., examples=["example@example.com"])


class ChangePasswordRequest(BaseModel):
    user_id: int = Field(..., examples=[1], title="User ID")
    old_password: SecretStr | None = Field(
        None,
        examples=["old_password"],
        min_length=8,
    )
    new_password: SecretStr = Field(
        ...,
        examples=["new_password"],
        title="New password",
        min_length=8,
    )
    reset_code: str | None = Field(
        None,
        examples=["reset_code"],
        pattern=r"^[A-Z\d]{10}$",
    )

    @field_validator("old_password")
    @classmethod
    def old_password_must_be_present(
        cls: type["ChangePasswordRequest"],
        v: SecretStr,
        info: FieldValidationInfo,
    ) -> SecretStr:
        if not v and not info.data.get("reset_code"):
            text_error = "must be present"
            raise ValueError(text_error)
        return v

    @field_validator("reset_code")
    @classmethod
    def reset_code_or_old_password_must_be_present(
        cls: type["ChangePasswordRequest"],
        v: SecretStr,
        info: FieldValidationInfo,
    ) -> SecretStr | None:
        if info.data.get("old_password") and v:
            return None
        return v
