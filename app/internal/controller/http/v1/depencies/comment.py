from typing import AsyncIterator

from fastapi import Depends
from sqlalchemy.orm import sessionmaker

from app.internal.usecase.comment import (
    CreateCommentUseCase,
    GetAllCommentsUseCase,
    GetCountCommentsUseCase,
    GetVideoCommentsUseCase,
)
from app.internal.usecase.repository.comment import PostgresCommentRepository
from app.pkg.postgres import get_session


async def create_pg_repository(
    *,
    db_session: AsyncIterator[sessionmaker] = Depends(get_session),
) -> PostgresCommentRepository:
    async with db_session.begin() as session:
        return PostgresCommentRepository(session)


def create_create_comment_usecase(
    *,
    repository: PostgresCommentRepository = Depends(create_pg_repository),
) -> CreateCommentUseCase:
    return CreateCommentUseCase(repository)


def create_get_video_comments_usecase(
    *,
    repository: PostgresCommentRepository = Depends(create_pg_repository),
) -> GetVideoCommentsUseCase:
    return GetVideoCommentsUseCase(repository)


def create_get_all_comments_usecase(
    *,
    repository: PostgresCommentRepository = Depends(create_pg_repository),
) -> GetAllCommentsUseCase:
    return GetAllCommentsUseCase(repository)


def create_get_count_comments_usecase(
    *,
    repository: PostgresCommentRepository = Depends(create_pg_repository),
) -> GetCountCommentsUseCase:
    return GetCountCommentsUseCase(repository)
