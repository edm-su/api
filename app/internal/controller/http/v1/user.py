from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    Security,
)
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr
from starlette import status

from app.internal.controller.http.v1.dependencies.auth import (
    CurrentUser,
    get_current_user,
    get_refresh_token_data,
)
from app.internal.controller.http.v1.dependencies.user import (
    create_activate_user_usecase,
    create_change_password_by_reset_code_usecase,
    create_change_password_usecase,
    create_create_user_usecase,
    create_reset_password_usecase,
    create_sign_in_usecase,
)
from app.internal.controller.http.v1.requests.user import (
    ActivateUserRequest,
    ChangePasswordRequest,
    CompleteResetPasswordRequest,
    PasswordResetRequest,
    SignUpRequest,
)
from app.internal.controller.http.v1.responses.user import (
    MeResponse,
    RefreshTokenResponse,
    SignInResponse,
    SignUpResponse,
)
from app.internal.entity.user import (
    AccessTokenDataCreator,
    ActivateUserDto,
    ChangePasswordByResetCodeDto,
    ChangePasswordDto,
    NewUserDto,
    RefreshTokenDataCreator,
    SignInDto,
    TokenData,
    User,
)
from app.internal.usecase.exceptions.user import UserError, UserNotFoundError
from app.internal.usecase.user import (
    ActivateUserUseCase,
    ChangePasswordByResetCodeUseCase,
    ChangePasswordUseCase,
    CreateUserUseCase,
    ResetPasswordUseCase,
    SignInUseCase,
)

router = APIRouter(tags=["Users"])


@router.post(
    "",
    summary="Sign up",
    status_code=status.HTTP_201_CREATED,
)
async def sign_up(
    request_data: SignUpRequest,
    usecase: Annotated[
        CreateUserUseCase,
        Depends(create_create_user_usecase),
    ],
) -> SignUpResponse:
    try:
        new_user = NewUserDto(
            username=request_data.username,
            email=request_data.email,
            password=request_data.password,
        )
        user = await usecase.execute(new_user)
    except UserError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    return SignUpResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
    )


@router.post(
    "/activate",
    summary="Activate user",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def activate(
    request_data: ActivateUserRequest,
    usecase: Annotated[
        ActivateUserUseCase,
        Depends(create_activate_user_usecase),
    ],
) -> None:
    code = ActivateUserDto(
        id=request_data.id,
        activation_code=request_data.activation_code,
    )
    try:
        await usecase.execute(code)
    except UserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/me",
    summary="Get me",
)
async def me(user: CurrentUser) -> MeResponse:
    return MeResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_admin=user.is_admin,
        is_banned=user.is_banned,
        created_at=user.created_at,
        last_login=user.last_login,
        last_login_ip=user.last_login_ip,
    )


@router.post(
    "/password/reset",
    summary="Request password reset",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def password_reset(
    request_data: PasswordResetRequest,
    usecase: Annotated[
        ResetPasswordUseCase,
        Depends(create_reset_password_usecase),
    ],
) -> None:
    try:
        await usecase.execute(request_data.email)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except UserError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.put(
    "/password/reset",
    summary=" Complete password reset",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def complete_password_reset(
    request_data: CompleteResetPasswordRequest,
    usecase: Annotated[
        ChangePasswordByResetCodeUseCase,
        Depends(create_change_password_by_reset_code_usecase),
    ],
) -> None:
    try:
        await usecase.execute(
            ChangePasswordByResetCodeDto(
                user_id=request_data.user_id,
                new_password=request_data.new_password,
                code=request_data.code,
            ),
        )
    except UserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.put(
    "/password",
    summary="Change password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    request_data: ChangePasswordRequest,
    usecase: Annotated[
        ChangePasswordUseCase,
        Depends(create_change_password_usecase),
    ],
    user: Annotated[
        User,
        Security(get_current_user, scopes=["user:change_password"]),
    ],
) -> None:
    try:
        await usecase.execute(
            ChangePasswordDto(
                user_id=user.id,
                old_password=request_data.old_password,
                new_password=request_data.new_password,
            ),
        )
    except UserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/sign-in",
    summary="Authentication",
)
async def sign_in(
    response: Response,
    request_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    usecase: Annotated[
        SignInUseCase,
        Depends(create_sign_in_usecase),
    ],
) -> SignInResponse:
    forbidden_scopes = ("user:activate", "user:refresh")

    for scope in forbidden_scopes:
        if scope in request_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You cannot request {scope} scope",
            )

    user = await usecase.execute(
        SignInDto(
            email=request_data.username,
            password=SecretStr(request_data.password),
        ),
    )

    token = TokenData(
        email=user.email,
        username=user.username,
        sub=user.id,
        is_admin=user.is_admin,
        scope=request_data.scopes,
    )

    access_token = AccessTokenDataCreator().factory(token)
    refresh_token = RefreshTokenDataCreator().factory(token)

    response.headers["Cache-Control"] = "no-store"
    return SignInResponse(
        access_token=access_token.get_jwt_token(),
        refresh_token=refresh_token.get_jwt_token(),
    )


@router.post(
    "/token",
    summary="Refresh token",
)
async def refresh_token(
    response: Response,
    _: Annotated[
        str,
        Query(
            ...,
            title="grant_type",
            pattern=r"^refresh_token$",
            alias="grant_type",
        ),
    ],
    token_data: Annotated[
        TokenData,
        Depends(get_refresh_token_data),
    ],
) -> RefreshTokenResponse:
    if "user:refresh" in token_data.scope:
        token_data.scope.remove("user:refresh")

    access_token = AccessTokenDataCreator().factory(token_data)
    refresh_token = RefreshTokenDataCreator().factory(token_data)

    response.headers["Cache-Control"] = "no-store"
    return RefreshTokenResponse(
        access_token=access_token.get_jwt_token(),
        refresh_token=refresh_token.get_jwt_token(),
    )
    refresh_token = RefreshTokenDataCreator().factory(token_data)

    response.headers["Cache-Control"] = "no-store"
    return RefreshTokenResponse(
        access_token=access_token.get_jwt_token(),
        refresh_token=refresh_token.get_jwt_token(),
    )
