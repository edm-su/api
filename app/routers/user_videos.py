from typing import Mapping

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app import auth
from app.depencies import create_pg_user_video_repository, find_video
from app.repositories.user_video import PostgresUserVideoRepository
from app.schemas.user import User
from app.schemas.video import PgVideo

router = APIRouter()


@router.post(
    "/videos/{slug}/like",
    tags=["Видео", "Пользователи"],
    summary="Добавление понравившегося видео",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def add_liked_video(
    pg_video: PgVideo = Depends(find_video),
    user: Mapping = Depends(auth.get_current_user),
    pg_user_video_repository: PostgresUserVideoRepository = Depends(
        create_pg_user_video_repository,
    ),
) -> None:
    user = User(**user)
    if await pg_user_video_repository.is_liked(user, pg_video):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Видео уже понравилось ранее",
        )
    await pg_user_video_repository.like_video(user, pg_video)


@router.delete(
    "/videos/{slug}/like",
    tags=["Видео", "Пользователи"],
    summary="Удаление понравившегося видео",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unlike_video(
    pg_video: PgVideo = Depends(find_video),
    user: Mapping = Depends(auth.get_current_user),
    ps_user_video_repository: PostgresUserVideoRepository = Depends(
        create_pg_user_video_repository,
    ),
) -> None:
    user = User(**user)
    if not await ps_user_video_repository.is_liked(user, pg_video):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Видео не понравилось ранее",
        )
    await ps_user_video_repository.unlike_video(user, pg_video)


@router.get(
    "/users/liked_videos",
    response_model=list[PgVideo],
    tags=["Видео", "Пользователи"],
    summary="Получить список понравившихся видео",
)
async def get_liked_videos(
    current_user: Mapping = Depends(auth.get_current_user),
    pg_user_video_repository: PostgresUserVideoRepository = Depends(
        create_pg_user_video_repository,
    ),
) -> list[PgVideo]:
    user = User(**current_user)
    return await pg_user_video_repository.get_liked_videos(user)
