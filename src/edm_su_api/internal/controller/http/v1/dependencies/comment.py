from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from edm_su_api.internal.usecase.comment import (
    CreateCommentUseCase,
    GetAllCommentsUseCase,
    GetCountCommentsUseCase,
    GetVideoCommentsUseCase,
)
from edm_su_api.internal.usecase.repository.comment import (
    PostgresCommentRepository,
)
from edm_su_api.pkg.postgres import get_session


async def create_pg_repository(
    *,
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> PostgresCommentRepository:
    return PostgresCommentRepository(session)


PgRepository = Annotated[
    PostgresCommentRepository,
    Depends(create_pg_repository),
]


def create_create_comment_usecase(
    *,
    repository: PgRepository,
) -> CreateCommentUseCase:
    return CreateCommentUseCase(repository)


def create_get_video_comments_usecase(
    *,
    repository: PgRepository,
) -> GetVideoCommentsUseCase:
    return GetVideoCommentsUseCase(repository)


def create_get_all_comments_usecase(
    *,
    repository: PgRepository,
) -> GetAllCommentsUseCase:
    return GetAllCommentsUseCase(repository)


def create_get_count_comments_usecase(
    *,
    repository: PgRepository,
) -> GetCountCommentsUseCase:
    return GetCountCommentsUseCase(repository)
