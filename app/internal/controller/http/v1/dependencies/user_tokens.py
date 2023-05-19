from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.internal.usecase.repository.user_tokens import (
    PostgresUserTokensRepository,
)
from app.internal.usecase.user_tokens import (
    CreateUserTokenUseCase,
    GetAllUserTokensUseCase,
    RevokeUserTokenUseCase,
)
from app.pkg.postgres import get_session


async def create_pg_repository(
    *,
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> PostgresUserTokensRepository:
    return PostgresUserTokensRepository(session)


PgRepository = Annotated[
    PostgresUserTokensRepository,
    Depends(create_pg_repository),
]


def create_create_user_token_usecase(
    *,
    repository: PgRepository,
) -> CreateUserTokenUseCase:
    return CreateUserTokenUseCase(repository)


def create_get_user_tokens_usecase(
    *,
    repository: PgRepository,
) -> GetAllUserTokensUseCase:
    return GetAllUserTokensUseCase(repository)


def create_revoke_user_token_usecase(
    *,
    repository: PgRepository,
) -> RevokeUserTokenUseCase:
    return RevokeUserTokenUseCase(repository)
