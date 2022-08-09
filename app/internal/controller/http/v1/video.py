import logging
from typing import (
    Mapping,
    AsyncIterator,
)

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette import status

from app import auth
from app.crud import video as video_crud
from app.depencies import (
    create_ms_video_repository,
    create_pg_video_repository,
    find_video,
)
from app.helpers import Paginator
from app.internal.entity.video import Video
from app.internal.usecase.repository.video import PostgresVideoRepository
from app.internal.usecase.video import (
    GetAllVideosUseCase,
    GetCountVideosUseCase,
)
from app.pkg.postgres import get_session
from app.repositories.video import (
    MeilisearchVideoRepository,
)
from app.schemas.video import CreateVideo, MeilisearchVideo, PgVideo

router = APIRouter()


async def create_pg_repository(
    *,
    db_session: AsyncIterator[sessionmaker] = Depends(get_session),
) -> PostgresVideoRepository:
    async with db_session.begin() as session:
        return PostgresVideoRepository(session)


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


@router.get(
    "/videos",
    response_model=list[Video],
    tags=["Видео"],
    summary="Получить список видео",
)
async def get_videos(
    response: Response,
    pagination: Paginator = Depends(Paginator),
    get_all_usecase: GetAllVideosUseCase = Depends(
        create_get_all_videos_usecase
    ),
    count_usecase: GetCountVideosUseCase = Depends(
        create_count_videos_usecase
    ),
) -> list[Video]:
    db_videos = await get_all_usecase.execute(
        offset=pagination.skip,
        limit=pagination.limit,
    )
    count = await count_usecase.execute()
    response.headers["X-Total-Count"] = str(count)
    return db_videos


@router.get(
    "/videos/{slug}",
    response_model=PgVideo,
    tags=["Видео"],
    summary="Получить видео",
)
async def read_video(db_video: Mapping = Depends(find_video)) -> Mapping:
    return db_video


@router.delete(
    "/videos/{slug}",
    tags=["Видео"],
    summary="Удаление видео",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_video(
    admin: Mapping = Depends(auth.get_current_admin),
    pg_video: PgVideo = Depends(find_video),
    ms_video_repository: MeilisearchVideoRepository = Depends(
        create_ms_video_repository,
    ),
    pg_video_repository: PostgresVideoRepository = Depends(
        create_pg_repository,
    ),
) -> None:
    await pg_video_repository.delete(pg_video.id)
    await ms_video_repository.delete(pg_video.id)


@router.get(
    "/videos/{slug}/related",
    response_model=list[PgVideo],
    tags=["Видео"],
    summary="Получить похожие видео",
    deprecated=True,
)
async def read_related_videos(
    pg_video: PgVideo = Depends(find_video),
    limit: int = Query(default=15, ge=1, le=50),
    user: Mapping = Depends(auth.get_current_user_or_guest),
) -> list[Mapping]:
    user_id = user["id"] if user else None

    return await video_crud.get_related_videos(
        title=pg_video.title,
        limit=limit,
        user_id=user_id,
    )


@router.post(
    "/videos",
    response_model=PgVideo,
    tags=["Видео"],
    summary="Добавить видео",
    status_code=status.HTTP_201_CREATED,
)
async def add_video(
    new_video: CreateVideo,
    admin: Mapping = Depends(auth.get_current_admin),
    pg_video_repository: PostgresVideoRepository = Depends(
        create_pg_repository,
    ),
    ms_video_repository: MeilisearchVideoRepository = Depends(
        create_ms_video_repository,
    ),
) -> PgVideo:
    errors = []

    if await pg_video_repository.get_by_slug(new_video.slug):
        errors.append("Такой slug уже занят")
    if await pg_video_repository.get_by_yt_id(new_video.yt_id):
        errors.append("Такой yt_id уже существует")
    if errors:
        raise HTTPException(409, errors)

    pg_video = await pg_video_repository.create(
        video=new_video,
    )
    ms_video = MeilisearchVideo(**pg_video.dict())
    await ms_video_repository.create(ms_video)
    return pg_video
