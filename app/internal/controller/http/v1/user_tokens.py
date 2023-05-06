from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field

from app.internal.controller.http.v1.dependencies.auth import get_current_admin
from app.internal.controller.http.v1.dependencies.user_tokens import (
    create_create_user_token_usecase,
    create_get_user_tokens_usecase,
    create_revoke_user_token_usecase,
)
from app.internal.entity.user import TokenData, User, UserToken, UserTokenDTO
from app.internal.usecase.exceptions.user_tokens import UserTokensError
from app.internal.usecase.user_tokens import (
    CreateUserTokenUseCase,
    GetAllUserTokensUseCase,
    RevokeUserTokenUseCase,
)


class CreateAPITokenRequest(BaseModel):
    name: str
    expired_at: datetime | None = Field(default=None)


class CreateAPITokenResponse(BaseModel):
    id: int
    name: str
    expired_at: datetime | None = Field(default=None)
    created_at: datetime
    token: str


class GetAllAPITokensResponse(BaseModel):
    tokens: list[UserToken | None]


router = APIRouter(tags=["User API Tokens"])


@router.post(
    "/",
    summary="Create api token",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateAPITokenResponse,
)
async def create_api_token(
    request_data: CreateAPITokenRequest,
    usecase: CreateUserTokenUseCase = Depends(
        create_create_user_token_usecase,
    ),
    admin: User = Depends(get_current_admin),
) -> CreateAPITokenResponse:
    data = UserTokenDTO(
        name=request_data.name,
        expired_at=request_data.expired_at,
    )
    token = await usecase.execute(data, admin)
    jwt_token_data = TokenData(
        id=admin.id,
        email=admin.email,
        username=admin.username,
        is_admin=admin.is_admin,
        token_id=token.id,
    )

    jwt_token = get_jwt_token(jwt_token_data, request_data.expired_at)

    return CreateAPITokenResponse(
        id=token.id,
        name=token.name,
        expired_at=token.expired_at,
        created_at=token.created_at,
        token=jwt_token,
    )


def get_jwt_token(
    jwt_token_data: TokenData,
    expired_at: datetime | None = None,
) -> str:
    if expired_at:
        delta = expired_at - datetime.utcnow()
        return jwt_token_data.get_jwt_token(delta)
    return jwt_token_data.get_jwt_token()


@router.get(
    "/",
    summary="Get all api tokens",
    status_code=status.HTTP_200_OK,
    response_model=list[GetAllAPITokensResponse],
)
async def get_all_api_tokens(
    usecase: GetAllUserTokensUseCase = Depends(
        create_get_user_tokens_usecase,
    ),
    admin: User = Depends(get_current_admin),
) -> GetAllAPITokensResponse:
    return GetAllAPITokensResponse(
        tokens=await usecase.execute(admin),
    )


@router.delete(
    "/{token_id}",
    summary="Revoke api token",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_api_token(
    token_id: int = Path(title="Token id"),
    usecase: RevokeUserTokenUseCase = Depends(
        create_revoke_user_token_usecase,
    ),
    admin: User = Depends(get_current_admin),
) -> None:
    try:
        await usecase.execute(token_id, admin)
    except UserTokensError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
