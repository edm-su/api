from typing import Mapping

from fastapi import APIRouter, Depends
from starlette import status

from app.auth import get_current_admin
from app.crud import token as token_crud
from app.helpers import generate_token
from app.schemas import token as token_schemas

router = APIRouter(prefix="/users/api_token", tags=["Токены", "Пользователи"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=token_schemas.Token,
)
async def create_token(
    token_info: token_schemas.TokenInfo,
    admin: Mapping = Depends(get_current_admin),
) -> token_schemas.Token:
    token = generate_token()
    await token_crud.add_token(token_info.name, token, admin["id"])
    return token_schemas.Token(token=token)
