from typing import Annotated

from fastapi import Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.internal.entity.video import Video
from app.internal.usecase.exceptions.video import VideoNotFoundError
from app.internal.usecase.repository.video import (
    MeilisearchVideoRepository,
    PostgresVideoRepository,
)
from app.internal.usecase.video import (
    CreateVideoUseCase,
    DeleteVideoUseCase,
    GetAllVideosUseCase,
    GetCountVideosUseCase,
    GetVideoBySlugUseCase,
)
from app.pkg.meilisearch import ms_client
from app.pkg.postgres import get_session


async def create_pg_repository(
    *,
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> PostgresVideoRepository:
    return PostgresVideoRepository(session)


PgRepository = Annotated[
    PostgresVideoRepository,
    Depends(create_pg_repository),
]


async def create_ms_repository() -> MeilisearchVideoRepository:
    return MeilisearchVideoRepository(ms_client)


MeilisearchRepository = Annotated[
    MeilisearchVideoRepository,
    Depends(create_ms_repository),
]


def create_get_all_videos_usecase(
    *,
    repository: PgRepository,
) -> GetAllVideosUseCase:
    return GetAllVideosUseCase(repository)


def create_count_videos_usecase(
    *,
    repository: PgRepository,
) -> GetCountVideosUseCase:
    return GetCountVideosUseCase(repository)


def create_get_video_by_slug_usecase(
    *,
    repository: PgRepository,
) -> GetVideoBySlugUseCase:
    return GetVideoBySlugUseCase(repository)


def create_delete_video_usecase(
    *,
    repository: PgRepository,
    ms_repository: MeilisearchRepository,
) -> DeleteVideoUseCase:
    return DeleteVideoUseCase(repository, ms_repository)


def create_create_video_usecase(
    *,
    repository: PgRepository,
    ms_repository: MeilisearchRepository,
) -> CreateVideoUseCase:
    return CreateVideoUseCase(repository, ms_repository)


async def find_video(
    slug: Annotated[
        str,
        Path,
    ],
    usecase: GetVideoBySlugUseCase = Depends(create_get_video_by_slug_usecase),
) -> Video:
    try:
        return await usecase.execute(slug)
    except VideoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


FindVideo = Annotated[Video, Depends(find_video)]
