from typing import Annotated
from uuid import uuid4

from pydantic import (
    BaseModel as Model,
)
from pydantic import (
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
)
from slugify import slugify
from typing_extensions import Self


class BaseModel(Model):
    model_config = ConfigDict(str_strip_whitespace=True)


class AttributeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SlugMixin(BaseModel):
    title: str
    slug: Annotated[str | None, Field(None, validate_default=True)] = None

    @field_validator("slug", mode="after")
    @classmethod
    def generate_slug(
        cls: type["SlugMixin"],
        v: str | None,
        info: ValidationInfo,
    ) -> str:
        if not v:
            return slugify(info.data["title"])
        return v

    def expand_slug(self: Self) -> None:
        expansion = uuid4().hex[:8]
        self.slug = f"{expansion}-{self.slug}"
