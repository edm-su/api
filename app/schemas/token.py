from pydantic import BaseModel, Field, SecretStr


class Token(BaseModel):
    token: SecretStr = Field()

    class Config:
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value()if v else None
        }


class TokenInfo(BaseModel):
    name: str = Field('', max_length=64)
