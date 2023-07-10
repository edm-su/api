from datetime import datetime

from pydantic import Field

from app.internal.entity.common import BaseModel


class CreateAPITokenRequest(BaseModel):
    name: str = Field(..., examples=["Token name"])
    expired_at: datetime | None = Field(
        default=None,
        examples=[datetime.now()],
    )
