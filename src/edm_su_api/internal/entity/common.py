from pydantic import BaseModel as Model
from pydantic import ConfigDict


class BaseModel(Model):
    model_config = ConfigDict(str_strip_whitespace=True)


class AttributeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
