from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.orm import sessionmaker

from app.internal.usecase.repository.user_videos import (
    PostgresUserVideosRepository,
)
from app.internal.usecase.user_videos import (
    GetUserVideosUseCase,
    LikeVideoUseCase,
    UnlikeVideoUseCase,
)
from app.pkg.postgres import get_session


async def create_pg_repository(
    *,
    db_session: AsyncIterator[sessionmaker] = Depends(get_session),
) -> PostgresUserVideosRepository:
    async with db_session.begin() as session:  # type: ignore[attr-defined]
        return PostgresUserVideosRepository(session)


def create_like_video_usecase(
    *,
    repository: PostgresUserVideosRepository = Depends(create_pg_repository),
) -> LikeVideoUseCase:
    return LikeVideoUseCase(repository)


def create_unlike_video_usecase(
    *,
    repository: PostgresUserVideosRepository = Depends(create_pg_repository),
) -> UnlikeVideoUseCase:
    return UnlikeVideoUseCase(repository)


def create_get_user_videos_usecase(
    *,
    repository: PostgresUserVideosRepository = Depends(create_pg_repository),
) -> GetUserVideosUseCase:
    return GetUserVideosUseCase(repository)
