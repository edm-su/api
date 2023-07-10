from datetime import datetime

from pydantic import BaseModel, Field


class CreateAPITokenResponse(BaseModel):
    id: int = Field(..., examples=[1])
    name: str = Field(..., examples=["Token name"])
    expired_at: datetime | None = Field(
        default=None,
        examples=[datetime.now()],
    )
    created_at: datetime = Field(..., examples=[datetime.now()])
    token: str = Field(
        ...,
        title="Token",
        examples=[
            (
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODk"
                "wIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJ"
                "SMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            ),
        ],
    )
