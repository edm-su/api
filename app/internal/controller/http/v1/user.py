import re
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    IPvAnyAddress,
    SecretStr,
    validator,
)
from starlette import status

from app.auth import get_current_user
from app.internal.controller.http.v1.depencies.user import (
    create_activate_user_usecase,
    create_change_password_by_reset_code_usecase,
    create_change_password_usecase,
    create_create_user_usecase,
    create_reset_password_usecase,
)
from app.internal.entity.user import (
    ActivateUserDto,
    ChangePasswordByResetCodeDto,
    ChangePasswordDto,
    NewUserDto,
    User,
)
from app.internal.usecase.exceptions.user import (
    NeedOldPasswordOrResetCodeError,
    UserError,
)
from app.internal.usecase.user import (
    ActivateUserUseCase,
    ChangePasswordByResetCodeUseCase,
    ChangePasswordUseCase,
    CreateUserUseCase,
    ResetPasswordUseCase,
)
from app.tasks import send_activate_email, send_recovery_email

router = APIRouter(tags=["Пользователи"])


class SignUpRequest(BaseModel):
    username: str = Field(..., example="user", title="Имя пользователя")
    email: EmailStr = Field(..., example="example@example.com", title="Email")
    password: SecretStr = Field(
        ...,
        example="password",
        title="Пароль",
        min_length=8,
    )

    @validator("username")
    def username_regexp(cls, v: str) -> str:  # noqa: ANN101, N805
        v = v.strip()
        if re.match(r"^[a-zA-Z0-9]+_?[a-zA-Z0-9]+$", v) is None:
            text_error = (
                "может содержать латинские символы, цифры, "
                "или знак подчёркивания. "
                "Начинаться и заканчиваться только латинским символом"
            )
            raise ValueError(text_error)
        return v


class SignUpResponse(BaseModel):
    id: int = Field(..., example=1, title="ID пользователя")
    username: str = Field(..., example="user", title="Имя пользователя")
    email: str = Field(..., example="example@example.com", title="Email")
    is_active: bool = Field(
        вуафгде=False,
        example=False,
        title="Активирован ли пользователь",
    )


class ActivateUserRequest(BaseModel):
    id: int = Field(..., example=1, title="ID пользователя")
    activation_code: SecretStr = Field(
        ...,
        example="activation_code",
        title="Код активации",
        regex=r"^[A-Z\d]{10}$",
        description="Код активации должен состоять из 10 символов",
    )


class MeResponse(BaseModel):
    id: int = Field(..., example=1, title="ID пользователя")
    username: str = Field(..., example="user", title="Имя пользователя")
    email: EmailStr = Field(..., example="example@example.com", title="Email")
    is_active: bool = Field(
        default=False,
        example=False,
        title="Активирован ли пользователь",
    )
    is_admin: bool = Field(
        default=False,
        example=False,
        title="Является ли пользователь администратором",
    )
    is_banned: bool = Field(
        default=False,
        example=False,
        title="Забанен ли пользователь",
    )
    created_at: datetime = Field(
        ...,
        example="2021-01-01T00:00:00",
        title="Время создания пользователя",
    )
    last_login: datetime | None = Field(
        ...,
        example="2021-01-01T00:00:00",
        title="Время последнего входа",
    )
    last_login_ip: IPvAnyAddress | None = Field(
        ...,
        example="127.0.0.1",
        title="IP адрес последнего входа",
        description="Адрес может быть IPv4 или IPv6",
    )


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., example="example@example.com", title="Email")


class ChangePasswordRequest(BaseModel):
    user_id: int = Field(..., example=1, title="ID пользователя")
    old_password: SecretStr | None = Field(
        None,
        example="old_password",
        title="Старый пароль",
        min_length=8,
    )
    new_password: SecretStr = Field(
        ...,
        example="new_password",
        title="Новый пароль",
        min_length=8,
    )
    reset_code: SecretStr | None = Field(
        None,
        example="reset_code",
        title="Код сброса пароля",
        regex=r"^[A-Z\d]{10}$",
        description="Код сброса пароля должен состоять из 10 символов",
    )

    @validator("old_password")
    def old_password_must_be_present(
        cls,  # noqa: N805, ANN101
        v: SecretStr,
        values: dict[str, Any],
    ) -> SecretStr:
        if not v and not values.get("reset_code"):
            text_error = "необходимо указать старый пароль или код сброса"
            raise ValueError(text_error)
        return v

    @validator("reset_code")
    def reset_code_or_old_password_must_be_present(
        cls,  # noqa: ANN101, N805
        v: SecretStr,
        values: dict[str, Any],
    ) -> SecretStr | None:
        if values.get("old_password") and v:
            return None
        return v


@router.post(
    "",
    response_model=SignUpResponse,
    summary="Регистрация пользователя",
)
async def sign_up(
    request_data: SignUpRequest,
    background_tasks: BackgroundTasks,
    usecase: CreateUserUseCase = Depends(create_create_user_usecase),
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
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    if not user.is_active and user.activation_code is not None:
        # TODO: Переделать на отправку через очередь
        background_tasks.add_task(
            send_activate_email,
            user.email,
            user.activation_code.get_secret_value(),
        )
    if not user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось создать пользователя",
        )
    return SignUpResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
    )


@router.post(
    "/activate/{activation_code}",
    summary="Активация пользователя",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def activate(
    request_data: ActivateUserRequest,
    usecase: ActivateUserUseCase = Depends(create_activate_user_usecase),
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


@router.post(
    "/me",
    summary="Получение информации о текущем пользователе",
    response_model=MeResponse,
)
async def me(user: User = Depends(get_current_user)) -> MeResponse:
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
    summary="Запрос на сброс пароля",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def password_reset(
    request_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    usecase: ResetPasswordUseCase = Depends(create_reset_password_usecase),
) -> None:
    try:
        code = await usecase.execute(request_data.email)
    except UserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e),
        ) from e
    # TODO: Переделать на отправку через очередь
    background_tasks.add_task(
        send_recovery_email,
        request_data.email,
        code.code.get_secret_value(),
    )


@router.put(
    "/password",
    summary="Смена пароля",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    request_data: ChangePasswordRequest,
    change_password_usecase: ChangePasswordUseCase = Depends(
        create_change_password_usecase,
    ),
    change_by_code_usecase: ChangePasswordByResetCodeUseCase = Depends(
        create_change_password_by_reset_code_usecase,
    ),
) -> None:
    try:
        if request_data.reset_code:
            await change_by_code_usecase.execute(
                ChangePasswordByResetCodeDto(
                    id=request_data.user_id,
                    code=request_data.reset_code,
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
