from typing import Mapping

from asyncpg import UniqueViolationError
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from starlette import status

from app import auth
from app.crud import video as video_crud
from app.helpers import Paginator
from app.repositories.video import meilisearch_video_repository
from app.schemas.video import CreateVideo, MeilisearchVideo, Video

router = APIRouter()


async def find_video(
    slug: str,
    user: None | Mapping = Depends(auth.get_current_user_or_guest),
) -> Mapping:
    user_id = user["id"] if user else None
    db_video = await video_crud.get_video_by_slug(slug=slug, user_id=user_id)

    if not db_video:
        raise HTTPException(status_code=404, detail="Видео не найдено")
    return db_video


@router.get(
    "/videos",
    response_model=list[Video],
    tags=["Видео"],
    summary="Получить список видео",
)
async def read_videos(
    response: Response,
    pagination: Paginator = Depends(Paginator),
    user: None | Mapping = Depends(auth.get_current_user_or_guest),
) -> list[Mapping]:
    user_id = user["id"] if user else None
    db_videos = await video_crud.get_videos(
        skip=pagination.skip,
        limit=pagination.limit,
        user_id=user_id,
    )
    count = await video_crud.get_videos_count()
    response.headers["X-Total-Count"] = str(count)
    return db_videos


@router.get(
    "/videos/{slug}",
    response_model=Video,
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
    db_video: Mapping = Depends(find_video),
) -> None:
    if await video_crud.delete_video(db_video["id"]):
        await meilisearch_video_repository.delete(db_video["id"])
    else:
        raise HTTPException(status_code=500, detail="Ошибка удаления видео")


@router.get(
    "/videos/{slug}/related",
    response_model=list[Video],
    tags=["Видео"],
    summary="Получить похожие видео",
)
async def read_related_videos(
    db_video: Mapping = Depends(find_video),
    limit: int = Query(default=15, ge=1, le=50),
    user: Mapping = Depends(auth.get_current_user_or_guest),
) -> list[Mapping]:
    user_id = user["id"] if user else None

    return await video_crud.get_related_videos(
        title=db_video["title"],
        limit=limit,
        user_id=user_id,
    )


@router.post(
    "/videos/{slug}/like",
    tags=["Видео", "Пользователи"],
    summary="Добавление понравившегося видео",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def add_liked_video(
    db_video: Mapping = Depends(find_video),
    user: Mapping = Depends(auth.get_current_user),
) -> None:
    try:
        await video_crud.like_video(
            user_id=user["id"], video_id=db_video["id"]
        )
    except UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Видео уже понравилось ранее",
        )


@router.delete(
    "/videos/{slug}/like",
    tags=["Видео", "Пользователи"],
    summary="Удаление понравившегося видео",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_liked_video(
    db_video: Mapping = Depends(find_video),
    user: Mapping = Depends(auth.get_current_user),
) -> None:
    if not await video_crud.dislike_video(
        user_id=user["id"],
        video_id=db_video["id"],
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Видео не найдено в понравившихся",
        )


@router.get(
    "/users/liked_videos",
    response_model=list[Video],
    tags=["Видео", "Пользователи"],
    summary="Получить список понравившихся видео",
)
async def get_liked_videos(
    current_user: Mapping = Depends(auth.get_current_user),
) -> list[Mapping]:
    return await video_crud.get_liked_videos(user_id=current_user["id"])


@router.post(
    "/videos",
    response_model=Video,
    tags=["Видео"],
    summary="Добавить видео",
    status_code=status.HTTP_201_CREATED,
)
async def add_video(
    new_video: CreateVideo,
    admin: Mapping = Depends(auth.get_current_admin),
) -> Video:
    errors = []

    if await video_crud.get_video_by_slug(new_video.slug):
        errors.append("Такой slug уже занят")
    if await video_crud.get_video_by_yt_id(new_video.yt_id):
        errors.append("Такой yt_id уже существует")
    if errors:
        raise HTTPException(409, errors)

    db_video = await video_crud.add_video(new_video)
    if not db_video:
        raise HTTPException(status_code=500, detail="Ошибка добавления видео")
    video = Video(**db_video)
    ms_video = MeilisearchVideo(**db_video)
    await meilisearch_video_repository.create(ms_video)
    return video
