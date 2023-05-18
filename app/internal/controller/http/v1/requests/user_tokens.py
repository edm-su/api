from datetime import datetime

from pydantic import BaseModel, Field


class CreateAPITokenRequest(BaseModel):
    name: str = Field(..., example="Token name", title="Token name")
    expired_at: datetime | None = Field(
        default=None,
        title="Token expired at",
        example=datetime.now(),
    )
