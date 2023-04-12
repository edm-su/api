from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.orm import sessionmaker

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
    db_session: AsyncIterator[sessionmaker] = Depends(get_session),
) -> PostgresUserTokensRepository:
    async with db_session.begin() as session:  # type: ignore[attr-defined]
        return PostgresUserTokensRepository(session)

def create_create_user_token_usecase(
    *,
    repository: PostgresUserTokensRepository = Depends(create_pg_repository),
) -> CreateUserTokenUseCase:
    return CreateUserTokenUseCase(repository)

def create_get_user_tokens_usecase(
    *,
    repository: PostgresUserTokensRepository = Depends(create_pg_repository),
) -> GetAllUserTokensUseCase:
    return GetAllUserTokensUseCase(repository)

def create_revoke_user_token_usecase(
    *,
    repository: PostgresUserTokensRepository = Depends(create_pg_repository),
) -> RevokeUserTokenUseCase:
    return RevokeUserTokenUseCase(repository)
