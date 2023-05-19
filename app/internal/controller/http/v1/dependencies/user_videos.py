from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

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
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> PostgresUserVideosRepository:
    return PostgresUserVideosRepository(session)


PgRepository = Annotated[
    PostgresUserVideosRepository,
    Depends(create_pg_repository),
]


def create_like_video_usecase(
    *,
    repository: PgRepository,
) -> LikeVideoUseCase:
    return LikeVideoUseCase(repository)


def create_unlike_video_usecase(
    *,
    repository: PgRepository,
) -> UnlikeVideoUseCase:
    return UnlikeVideoUseCase(repository)


def create_get_user_videos_usecase(
    *,
    repository: PgRepository,
) -> GetUserVideosUseCase:
    return GetUserVideosUseCase(repository)
