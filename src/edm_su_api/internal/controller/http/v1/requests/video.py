from datetime import date, datetime, timezone
from typing import Annotated

from pydantic import Field

from edm_su_api.internal.entity.common import BaseModel


class UpdateVideoRequest(BaseModel):
    title: str | None = Field(None, title="Video title", examples=["New title"])
    date: Annotated[
        date | None,
        Field(
            None,
            title="Publication date",
            examples=["2025-06-29"],
            le=datetime.now(timezone.utc).date(),
        ),
    ]
    is_blocked_in_russia: bool | None = Field(
        None, title="Blocked in Russia", examples=[False]
    )
