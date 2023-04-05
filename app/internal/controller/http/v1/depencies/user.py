from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.orm import sessionmaker

from app.internal.usecase.repository.user import PostgresUserRepository
from app.internal.usecase.user import (
    ActivateUserUseCase,
    ChangePasswordByResetCodeUseCase,
    ChangePasswordUseCase,
    CreateUserUseCase,
    GetUserByUsernameUseCase,
    ResetPasswordUseCase,
)
from app.pkg.postgres import get_session


async def create_pg_repository(
    *,
    db_session: AsyncIterator[sessionmaker] = Depends(get_session),
) -> PostgresUserRepository:
    async with db_session.begin() as session:  # type: ignore[attr-defined]
        return PostgresUserRepository(session)


def create_create_user_usecase(
    *,
    repository: PostgresUserRepository = Depends(create_pg_repository),
) -> CreateUserUseCase:
    return CreateUserUseCase(repository)


def create_activate_user_usecase(
    *,
    repository: PostgresUserRepository = Depends(create_pg_repository),
) -> ActivateUserUseCase:
    return ActivateUserUseCase(repository)


def create_get_user_by_username_usecase(
    *,
    repository: PostgresUserRepository = Depends(create_pg_repository),
) -> GetUserByUsernameUseCase:
    return GetUserByUsernameUseCase(repository)


def create_reset_password_usecase(
    *,
    repository: PostgresUserRepository = Depends(create_pg_repository),
) -> ResetPasswordUseCase:
    return ResetPasswordUseCase(repository)


def create_change_password_usecase(
    *,
    repository: PostgresUserRepository = Depends(create_pg_repository),
) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(repository)


def create_change_password_by_reset_code_usecase(
    *,
    repository: PostgresUserRepository = Depends(create_pg_repository),
) -> ChangePasswordByResetCodeUseCase:
    return ChangePasswordByResetCodeUseCase(repository)
