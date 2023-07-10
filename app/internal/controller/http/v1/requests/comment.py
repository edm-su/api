from pydantic import Field

from app.internal.entity.common import BaseModel


class NewCommentRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=120,
        examples=["Comment text"],
    )
