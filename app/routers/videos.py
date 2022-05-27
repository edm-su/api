from collections.abc import Mapping

from databases.interfaces import Record
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from starlette import status

from app import auth
from app.crud import video as video_crud
from app.depencies import (
    create_ms_video_repository,
    create_pg_video_repository,
    find_video,
)
from app.helpers import Paginator
from app.repositories.video import (
    MeilisearchVideoRepository,
    PostgresVideoRepository,
)
from app.schemas.video import CreateVideo, MeilisearchVideo, PgVideo

router = APIRouter()


@router.get(
    "/videos",
    response_model=list[PgVideo],
    tags=["Видео"],
    summary="Получить список видео",
)
async def read_videos(
    response: Response,
    pagination: Paginator = Depends(Paginator),
    pg_video_repository: PostgresVideoRepository = Depends(
        create_pg_video_repository,
    ),
) -> list[PgVideo | None]:
    db_videos = await pg_video_repository.get_all(
        offset=pagination.skip,
        limit=pagination.limit,
    )
    count = await pg_video_repository.count()
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
    admin: Mapping = Depends(auth.get_current_admin),  # noqa: ARG001
    pg_video: PgVideo = Depends(find_video),
    ms_video_repository: MeilisearchVideoRepository = Depends(
        create_ms_video_repository,
    ),
    pg_video_repository: PostgresVideoRepository = Depends(
        create_pg_video_repository,
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
) -> list[Record]:
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
    admin: Mapping = Depends(auth.get_current_admin),  # noqa: ARG001
    pg_video_repository: PostgresVideoRepository = Depends(
        create_pg_video_repository,
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
