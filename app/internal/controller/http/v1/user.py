from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Response,
)
from pydantic import (
    SecretStr,
)
from starlette import status

from app.internal.controller.http.tasks import (
    send_activate_email,
    send_recovery_email,
)
from app.internal.controller.http.v1.dependencies.auth import (
    CurrentUser,
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
    PasswordResetRequest,
    SignInRequest,
    SignUpRequest,
)
from app.internal.controller.http.v1.responses.user import (
    MeResponse,
    SignInResponse,
    SignUpResponse,
)
from app.internal.entity.user import (
    ActivateUserDto,
    ChangePasswordByResetCodeDto,
    ChangePasswordDto,
    NewUserDto,
    SignInDto,
    TokenData,
)
from app.internal.usecase.exceptions.user import (
    NeedOldPasswordOrResetCodeError,
    UserError,
    UserNotFoundError,
)
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
    background_tasks: BackgroundTasks,
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
    if not user.is_active and user.activation_code is not None:
        # TODO: Переделать на отправку через очередь
        background_tasks.add_task(
            send_activate_email,
            user.email,
            user.activation_code.get_secret_value(),
        )
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
        activation_code=SecretStr(request_data.activation_code),
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
    background_tasks: BackgroundTasks,
    usecase: Annotated[
        ResetPasswordUseCase,
        Depends(create_reset_password_usecase),
    ],
) -> None:
    try:
        code = await usecase.execute(request_data.email)
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
    # TODO: Переделать на отправку через очередь
    background_tasks.add_task(
        send_recovery_email,
        request_data.email,
        code.code.get_secret_value(),
    )


@router.put(
    "/password",
    summary="Change password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    request_data: ChangePasswordRequest,
    change_password_usecase: Annotated[
        ChangePasswordUseCase,
        Depends(create_change_password_usecase),
    ],
    change_by_code_usecase: Annotated[
        ChangePasswordByResetCodeUseCase,
        Depends(create_change_password_by_reset_code_usecase),
    ],
) -> None:
    try:
        if request_data.reset_code:
            await change_by_code_usecase.execute(
                ChangePasswordByResetCodeDto(
                    id=request_data.user_id,
                    code=SecretStr(request_data.reset_code),
                    new_password=request_data.new_password,
                ),
            )
        elif request_data.old_password:
            await change_password_usecase.execute(
                ChangePasswordDto(
                    id=request_data.user_id,
                    old_password=request_data.old_password,
                    new_password=request_data.new_password,
                ),
            )
        else:
            raise NeedOldPasswordOrResetCodeError
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
    request_data: SignInRequest,
    usecase: Annotated[
        SignInUseCase,
        Depends(create_sign_in_usecase),
    ],
) -> SignInResponse:
    user = await usecase.execute(
        SignInDto(
            email=request_data.email,
            password=request_data.password,
        ),
    )

    token = TokenData(
        email=user.email,
        username=user.username,
        id=user.id,
        is_admin=user.is_admin,
    )

    response.headers["Cache-Control"] = "no-store"
    if request_data.remember_me:
        return SignInResponse(
            access_token=SecretStr(token.access_token()),
            refresh_token=SecretStr(token.refresh_token()),
        )
    return SignInResponse(
        access_token=SecretStr(token.access_token()),
    )
