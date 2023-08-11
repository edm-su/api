from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.internal.controller.http.v1.dependencies.auth import CurrentAdmin
from app.internal.controller.http.v1.dependencies.user_tokens import (
    create_create_user_token_usecase,
    create_get_user_tokens_usecase,
    create_revoke_user_token_usecase,
)
from app.internal.controller.http.v1.requests.user_tokens import (
    CreateAPITokenRequest,
)
from app.internal.controller.http.v1.responses.user_tokens import (
    CreateAPITokenResponse,
)
from app.internal.entity.user import (
    ApiTokenDataCreator,
    TokenData,
    UserToken,
    UserTokenDTO,
)
from app.internal.usecase.exceptions.user_tokens import UserTokenNotFoundError
from app.internal.usecase.user_tokens import (
    CreateUserTokenUseCase,
    GetAllUserTokensUseCase,
    RevokeUserTokenUseCase,
)

router = APIRouter(tags=["User API Tokens"])


@router.post(
    "",
    summary="Create api token",
    status_code=status.HTTP_201_CREATED,
)
async def create_api_token(
    admin: CurrentAdmin,
    request_data: CreateAPITokenRequest,
    usecase: Annotated[
        CreateUserTokenUseCase,
        Depends(create_create_user_token_usecase),
    ],
) -> CreateAPITokenResponse:
    data = UserTokenDTO(
        name=request_data.name,
        expired_at=request_data.expired_at,
    )
    token = await usecase.execute(data, admin)
    jwt_token_data = TokenData(
        sub=admin.id,
        email=admin.email,
        username=admin.username,
        is_admin=admin.is_admin,
        token_id=token.id,
    )

    api_token = ApiTokenDataCreator().factory(jwt_token_data)
    if request_data.expired_at:
        api_token.exp = request_data.expired_at

    return CreateAPITokenResponse(
        id=token.id,
        name=token.name,
        expired_at=token.expired_at,
        created_at=token.created_at,
        token=api_token.get_jwt_token(),
    )


@router.get(
    "",
    summary="Get all api tokens",
)
async def get_all_api_tokens(
    admin: CurrentAdmin,
    usecase: Annotated[
        GetAllUserTokensUseCase,
        Depends(create_get_user_tokens_usecase),
    ],
) -> list[UserToken]:
    return await usecase.execute(admin)


@router.delete(
    "/{token_id}",
    summary="Revoke api token",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_api_token(
    admin: CurrentAdmin,
    usecase: Annotated[
        RevokeUserTokenUseCase,
        Depends(create_revoke_user_token_usecase),
    ],
    token_id: Annotated[
        int,
        Path,
    ],
) -> None:
    try:
        await usecase.execute(token_id, admin)
    except UserTokenNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
