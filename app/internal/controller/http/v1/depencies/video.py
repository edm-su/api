from typing import AsyncIterator

from fastapi import Depends, HTTPException
from sqlalchemy.orm import sessionmaker
from starlette import status

from app.internal.entity.video import Video
from app.internal.usecase.exceptions.video import VideoNotFoundException
from app.internal.usecase.repository.video import (
    PostgresVideoRepository,
    MeilisearchVideoRepository,
)
from app.internal.usecase.video import (
    GetAllVideosUseCase,
    GetCountVideosUseCase,
    GetVideoBySlugUseCase,
    DeleteVideoUseCase,
    CreateVideoUseCase,
)
from app.meilisearch import ms_client
from app.pkg.postgres import get_session


async def create_pg_repository(
    *,
    db_session: AsyncIterator[sessionmaker] = Depends(get_session),
) -> PostgresVideoRepository:
    async with db_session.begin() as session:
        return PostgresVideoRepository(session)


async def create_ms_repository() -> MeilisearchVideoRepository:
    return MeilisearchVideoRepository(ms_client)


def create_get_all_videos_usecase(
    *,
    repository: PostgresVideoRepository = Depends(create_pg_repository),
) -> GetAllVideosUseCase:
    return GetAllVideosUseCase(repository)


def create_count_videos_usecase(
    *,
    repository: PostgresVideoRepository = Depends(create_pg_repository),
) -> GetCountVideosUseCase:
    return GetCountVideosUseCase(repository)


def create_get_video_by_slug_usecase(
    *,
    repository: PostgresVideoRepository = Depends(create_pg_repository),
) -> GetVideoBySlugUseCase:
    return GetVideoBySlugUseCase(repository)


def create_delete_video_usecase(
    *,
    repository: PostgresVideoRepository = Depends(create_pg_repository),
    ms_repository: MeilisearchVideoRepository = Depends(create_ms_repository),
) -> DeleteVideoUseCase:
    return DeleteVideoUseCase(repository, ms_repository)


def create_create_video_usecase(
    *,
    repository: PostgresVideoRepository = Depends(create_pg_repository),
    ms_repository: MeilisearchVideoRepository = Depends(create_ms_repository),
) -> CreateVideoUseCase:
    return CreateVideoUseCase(repository, ms_repository)


async def find_video(
    slug: str,
    usecase: GetVideoBySlugUseCase = Depends(create_get_video_by_slug_usecase),
) -> Video:
    try:
        return await usecase.execute(slug)
    except VideoNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        )
