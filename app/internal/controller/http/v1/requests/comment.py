from pydantic import BaseModel, Field


class NewCommentRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=120,
        title="Text",
        example="Comment text",
    )
