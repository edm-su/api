from datetime import datetime

from pydantic import BaseModel, Field


class CreateAPITokenResponse(BaseModel):
    id: int = Field(..., example=1, title="Token id")
    name: str = Field(..., example="Token name", title="Token name")
    expired_at: datetime | None = Field(
        default=None,
        title="Token expired at",
        example=datetime.now(),
    )
    created_at: datetime = Field(
        ...,
        title="Token created at",
        example=datetime.now(),
    )
    token: str = Field(
        ...,
        title="Token",
        example=(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODk"
            "wIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJ"
            "SMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        ),
    )
