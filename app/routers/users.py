from typing import Mapping

import fastapi
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from starlette import status

from app.auth import authenticate_user, create_access_token, get_current_user
from app.crud import user
from app.helpers import get_password_hash
from app.schemas.user import CreateUser, MyUser, Token, User, UserPassword
from app.tasks import send_activate_email, send_recovery_email

router = fastapi.APIRouter()


@router.post(
    "/users",
    tags=["Пользователи"],
    summary="Регистрация пользователя",
    response_model=MyUser,
)
async def user_register(
        new_user: CreateUser,
        background_tasks: fastapi.BackgroundTasks,
) -> None | Mapping:
    if await user.get_user_by_email(new_user.email):
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой email уже существует",
        )

    if await user.get_user_by_username(new_user.username):
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя пользователя занято",
        )

    db_user = await user.create_user(
        username=new_user.username,
        email=new_user.email,
        password=new_user.password,
    )
    if db_user:
        background_tasks.add_task(
            send_activate_email,
            db_user["email"],
            db_user["activation_code"],
        )
    return db_user


@router.post(
    "/users/activate/{code}",
    tags=["Пользователи"],
    summary="Активация учётной записи",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def user_activate(
        code: str = fastapi.Query(..., regex=r"^[A-Z\d]{10}$"),
) -> None:
    if not await user.activate_user(code=code):
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код активации",
        )
    return None


@router.post(
    "/users/token",
    response_model=Token,
    tags=["Пользователи"],
    summary="Авторизация и получение access_token",
)
async def login(
        form_data: OAuth2PasswordRequestForm = fastapi.Depends(),
) -> dict[str, str | bytes]:
    db_user = await authenticate_user(
        username=form_data.username,
        password=form_data.password,
    )

    if not db_user:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверное имя пользователя или пароль",
        )
    if not db_user["is_active"]:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Учётная запись не подтверждена",
        )
    if db_user["is_banned"]:
        raise fastapi.HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Учётная запись заблокирована",
        )

    access_token = create_access_token(data={"sub": db_user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/users/me",
    response_model=MyUser,
    tags=["Пользователи"],
    summary="Получение данных пользователя",
)
async def read_current_user(
        current_user: MyUser = fastapi.Depends(get_current_user),
) -> MyUser:
    return current_user


@router.post(
    "/users/password-recovery/{email}",
    tags=["Пользователи"],
    summary="Восстановление пароля",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def user_recovery(
        email: EmailStr,
        background_tasks: fastapi.BackgroundTasks,
) -> None:
    db_user = await user.get_user_by_email(email=email)
    if not db_user:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким email не найден",
        )
    code = await user.generate_recovery_user_code(user_id=db_user["id"])
    background_tasks.add_task(send_recovery_email, db_user["email"], code)


@router.put(
    "/users/password",
    tags=["Пользователи"],
    summary="Изменение пароля",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
        new_password: UserPassword,
        old_password: str = fastapi.Body(..., min_length=6),
        current_user: Mapping = fastapi.Depends(get_current_user),
) -> None:
    if get_password_hash(old_password) == current_user["password"]:
        await user.change_password(
            user_id=current_user["id"],
            password=new_password.password,
        )
    else:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Старый пароль неверный",
        )


@router.put(
    "/users/reset-password/{code}",
    tags=["Пользователи"],
    summary="Сброс пароля",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def complete_recovery(code: str, password: UserPassword) -> None:
    db_user = await user.get_user_by_recovery_code(code)
    if not db_user:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код или истёк срок действия",
        )

    await user.change_password(
        user_id=db_user["id"],
        password=password.password,
        recovery=True,
    )


@router.get(
    "/users/{id}",
    response_model=User,
    tags=["Пользователи"],
    summary="Получение информации о пользователе",
)
async def read_user(id_: int = fastapi.Path(..., alias="id")) -> Mapping:
    db_user = await user.get_user_by_id(id_)
    if not db_user:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return db_user
