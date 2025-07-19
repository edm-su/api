from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class UpdatePostRequest(BaseModel):
    """Request model for updating a post"""

    title: str | None = Field(None, min_length=1, max_length=100)
    annotation: str | None = Field(None, max_length=500, description="Post annotation")
    text: dict[str, Any] | None = None
    thumbnail: str | None = Field(None, description="URL of the post thumbnail image")
    published_at: datetime | None = Field(None, description="Publication date and time")
    save_history: bool = Field(default=False, description="Save record in edit history")
    history_description: str | None = Field(
        None,
        description=(
            "Description of changes for history (required when save_history=True)"
        ),
    )

    @model_validator(mode="after")
    def validate_history_description(self: Self) -> Self:
        if self.save_history and not self.history_description:
            msg = "history_description is required when save_history is True"
            raise ValueError(msg)
        return self
