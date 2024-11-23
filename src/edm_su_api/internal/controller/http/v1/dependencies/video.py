from typing import Annotated

from fastapi import Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from edm_su_api.internal.controller.http.v1.dependencies.permissions import (
    SpiceDBPermissionsRepo,
)
from edm_su_api.internal.entity.video import Video
from edm_su_api.internal.usecase.exceptions.video import VideoNotFoundError
from edm_su_api.internal.usecase.repository.video import (
    MeilisearchVideoRepository,
    PostgresVideoRepository,
)
from edm_su_api.internal.usecase.video import (
    CreateVideoUseCase,
    DeleteVideoUseCase,
    GetAllVideosUseCase,
    GetCountVideosUseCase,
    GetVideoBySlugUseCase,
)
from edm_su_api.pkg.meilisearch import ms_client
from edm_su_api.pkg.postgres import get_session


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
    spicedb_repository: SpiceDBPermissionsRepo,
) -> DeleteVideoUseCase:
    return DeleteVideoUseCase(repository, ms_repository, spicedb_repository)


def create_create_video_usecase(
    *,
    repository: PgRepository,
    ms_repository: MeilisearchRepository,
    spicedb_repository: SpiceDBPermissionsRepo,
) -> CreateVideoUseCase:
    return CreateVideoUseCase(repository, ms_repository, spicedb_repository)


async def find_video(
    slug: Annotated[
        str,
        Path,
    ],
    usecase: Annotated[
        GetVideoBySlugUseCase,
        Depends(create_get_video_by_slug_usecase),
    ],
) -> Video:
    try:
        return await usecase.execute(slug)
    except VideoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


FindVideo = Annotated[Video, Depends(find_video)]
