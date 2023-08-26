from pydantic import BaseModel, Field, computed_field
from typing_extensions import Self


class User(BaseModel):
    id: str = Field("Anonymous")

    @computed_field  # type: ignore[misc]
    @property
    def is_guest(self: Self) -> bool:
        return self.id == "Anonymous"
