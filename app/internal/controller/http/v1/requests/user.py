import re

from pydantic import (
    EmailStr,
    Field,
    SecretStr,
    field_validator,
)

from app.internal.entity.common import BaseModel
from app.internal.entity.user import (
    ChangePassword,
    ChangePasswordByResetCodeDto,
    OldPassword,
)


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


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., examples=["example@example.com"])


class CompleteResetPasswordRequest(ChangePasswordByResetCodeDto):
    pass


class ChangePasswordRequest(ChangePassword, OldPassword):
    pass
