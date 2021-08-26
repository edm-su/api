from typing import List, Mapping, Optional

from asyncpg import UniqueViolationError
from fastapi import APIRouter, HTTPException, Depends, Response, Query
from starlette import status

from app import auth
from app.crud import video
from app.helpers import Paginator
from app.schemas.video import Video, CreateVideo

router = APIRouter()


async def find_video(
        slug: str,
        user: Optional[Mapping] = Depends(auth.get_current_user_or_guest),
) -> Mapping:
    user_id = user['id'] if user else None
    db_video = await video.get_video_by_slug(slug=slug, user_id=user_id)

    if not db_video:
        raise HTTPException(status_code=404, detail='Видео не найдено')
    return db_video


@router.get(
    '/videos',
    response_model=List[Video],
    tags=['Видео'],
    summary='Получить список видео',
)
async def read_videos(
        response: Response,
        pagination: Paginator = Depends(Paginator),
        user: Optional[Mapping] = Depends(auth.get_current_user_or_guest),
) -> List[Mapping]:
    user_id = user['id'] if user else None
    db_videos = await video.get_videos(
        skip=pagination.skip,
        limit=pagination.limit,
        user_id=user_id,
    )
    count = await video.get_videos_count()
    response.headers['X-Total-Count'] = str(count)
    return db_videos


@router.get(
    '/videos/{slug}',
    response_model=Video,
    tags=['Видео'],
    summary='Получить видео',
)
async def read_video(db_video: Mapping = Depends(find_video)) -> Mapping:
    return db_video


@router.delete(
    '/videos/{slug}',
    tags=['Видео'],
    summary='Удаление видео',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_video(
        admin: Mapping = Depends(auth.get_current_admin),
        db_video: Mapping = Depends(find_video),
) -> None:
    if not await video.delete_video(video_id=db_video['id']):
        raise HTTPException(400, 'При удалении произошла ошибка')


@router.get(
    '/videos/{slug}/related',
    response_model=List[Video],
    tags=['Видео'],
    summary='Получить похожие видео',
)
async def read_related_videos(
        db_video: Mapping = Depends(find_video),
        limit: int = Query(default=15, ge=1, le=50),
        user: Mapping = Depends(auth.get_current_user_or_guest),
) -> List[Mapping]:
    user_id = user['id'] if user else None

    return await video.get_related_videos(
        title=db_video['title'],
        limit=limit,
        user_id=user_id,
    )


@router.post(
    '/videos/{slug}/like',
    tags=['Видео', 'Пользователи'],
    summary='Добавление понравившегося видео',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def add_liked_video(
        db_video: Mapping = Depends(find_video),
        user: Mapping = Depends(auth.get_current_user),
) -> None:
    try:
        await video.like_video(user_id=user['id'], video_id=db_video['id'])
    except UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Видео уже понравилось ранее',
        )


@router.delete(
    '/videos/{slug}/like',
    tags=['Видео', 'Пользователи'],
    summary='Удаление понравившегося видео',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_liked_video(
        db_video: Mapping = Depends(find_video),
        user: Mapping = Depends(auth.get_current_user),
) -> None:
    if not await video.dislike_video(
            user_id=user['id'],
            video_id=db_video['id'],
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Видео не найдено в понравившихся',
        )


@router.get(
    '/users/liked_videos',
    response_model=List[Video],
    tags=['Видео', 'Пользователи'],
    summary='Получить список понравившихся видео',
)
async def get_liked_videos(
        current_user: Mapping = Depends(auth.get_current_user),
) -> List[Mapping]:
    return await video.get_liked_videos(user_id=current_user['id'])


@router.post(
    '/videos',
    response_model=Video,
    tags=['Видео'],
    summary='Добавить видео',
    status_code=status.HTTP_201_CREATED,
)
async def add_video(
        new_video: CreateVideo,
        admin: Mapping = Depends(auth.get_current_admin),
) -> Optional[Mapping]:
    errors = []
    if await video.get_video_by_slug(new_video.slug):
        errors.append('Такой slug уже занят')
    if await video.get_video_by_yt_id(new_video.yt_id):
        errors.append('Такой yt_id уже существует')
    if errors:
        raise HTTPException(409, errors)
    return await video.add_video(new_video)
