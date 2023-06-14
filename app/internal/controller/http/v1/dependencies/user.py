from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.internal.usecase.repository.user import PostgresUserRepository
from app.internal.usecase.user import (
    ActivateUserUseCase,
    ChangePasswordByResetCodeUseCase,
    ChangePasswordUseCase,
    CreateUserUseCase,
    GetUserByUsernameUseCase,
    ResetPasswordUseCase,
    SignInUseCase,
)
from app.pkg.nats import nats_client
from app.pkg.postgres import get_session


async def create_pg_repository(
    *,
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> PostgresUserRepository:
    return PostgresUserRepository(session)


PgRepository = Annotated[
    PostgresUserRepository,
    Depends(create_pg_repository),
]


def create_create_user_usecase(
    *,
    repository: PgRepository,
) -> CreateUserUseCase:
    return CreateUserUseCase(repository, nats_client)


def create_activate_user_usecase(
    *,
    repository: PgRepository,
) -> ActivateUserUseCase:
    return ActivateUserUseCase(repository, nats_client)


def create_get_user_by_username_usecase(
    *,
    repository: PgRepository,
) -> GetUserByUsernameUseCase:
    return GetUserByUsernameUseCase(repository, nats_client)


def create_reset_password_usecase(
    *,
    repository: PgRepository,
) -> ResetPasswordUseCase:
    return ResetPasswordUseCase(repository, nats_client)


def create_change_password_usecase(
    *,
    repository: PgRepository,
) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(repository, nats_client)


def create_change_password_by_reset_code_usecase(
    *,
    repository: PgRepository,
) -> ChangePasswordByResetCodeUseCase:
    return ChangePasswordByResetCodeUseCase(repository, nats_client)


def create_sign_in_usecase(
    *,
    repository: PgRepository,
) -> SignInUseCase:
    return SignInUseCase(repository, nats_client)
