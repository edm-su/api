import typing
from typing import List

from asyncpg import UniqueViolationError
from fastapi import APIRouter, HTTPException, Depends, Response, Query
from starlette import status

from app.auth import get_current_user_or_guest, get_current_admin, get_current_user
from app.crud import video
from app.db import videos
from app.helpers import Paginator
from app.schemas.video import Video

router = APIRouter()


async def find_video(slug: str, user: typing.Optional[dict] = Depends(get_current_user_or_guest)) -> typing.Mapping:
    db_video = await video.get_video_by_slug(slug=slug, user_id=user['id'])
    if db_video:
        return db_video
    else:
        raise HTTPException(status_code=404, detail='Видео не найдено')


@router.get('/videos/', response_model=List[Video], tags=['Видео'], summary='Получить список видео')
async def read_videos(response: Response, pagination: Paginator = Depends(Paginator),
                      user: typing.Optional[dict] = Depends(get_current_user_or_guest)):
    if user:
        db_videos = await video.get_videos(skip=pagination.skip, limit=pagination.limit, user_id=user['id'])
    else:
        db_videos = await video.get_videos(skip=pagination.skip, limit=pagination.limit)
    count = await video.get_videos_count()
    response.headers['X-Total-Count'] = str(count)
    return db_videos


@router.get('/videos/{slug}', response_model=Video, tags=['Видео'], summary='Получить видео')
async def read_video(db_video: videos = Depends(find_video)):
    return db_video


@router.delete('/videos/{slug}', tags=['Видео'], summary='Удаление видео', status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(admin: dict = Depends(get_current_admin), db_video: dict = Depends(find_video)):
    if await video.delete_video(video_id=db_video['id']):
        return {}
    else:
        raise HTTPException(400, 'При удалении произошла ошибка')


@router.get('/videos/{slug}/related', response_model=List[Video], tags=['Видео'],
            summary='Получить похожие видео')
async def read_related_videos(db_video: videos = Depends(find_video), limit: int = Query(default=15, ge=1, le=50),
                              user: dict = Depends(get_current_user_or_guest)):
    return await video.get_related_videos(title=db_video['title'], limit=limit, user_id=user['id'])


@router.post('/videos/{slug}/like', tags=['Видео', 'Пользователи'], summary='Добавление понравившегося видео',
             status_code=status.HTTP_204_NO_CONTENT)
async def add_liked_video(db_video: dict = Depends(find_video), user: dict = Depends(get_current_user)):
    try:
        await video.like_video(user_id=user['id'], video_id=db_video['id'])
        return {}
    except UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Видео уже понравилось ранее')


@router.delete('/videos/{slug}/like', tags=['Видео', 'Пользователи'],
               summary='Удаление понравившегося видео', status_code=status.HTTP_204_NO_CONTENT)
async def delete_liked_video(db_video: dict = Depends(find_video), user: dict = Depends(get_current_user)):
    if not await video.dislike_video(user_id=user['id'], video_id=db_video['id']):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Видео не найдено в понравившихся')
    return {}


@router.get('/users/liked_videos', response_model=List[Video],
            tags=['Видео', 'Пользователи'], summary='Получить список понравившихся видео')
async def get_liked_videos(current_user: dict = Depends(get_current_user)):
    return await video.get_liked_videos(user_id=current_user['id'])
