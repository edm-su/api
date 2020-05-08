from typing import List

from fastapi import APIRouter, HTTPException, Depends, Response, Query

from app.crud import channel, video
from app.db import channels
from app.helpers import Paginator
from app.schemas.channel import Channel
from app.schemas.video import Video

router = APIRouter()


async def find_channel(slug: str):
    db_channel = await channel.get_channel_by_slug(slug=slug)
    if db_channel:
        return db_channel
    else:
        raise HTTPException(status_code=404, detail='Канал не найден')


@router.get('/channels/', response_model=List[Channel], tags=['Каналы'], summary='Получить список каналов')
async def read_channels(response: Response,
                        pagination: Paginator = Depends(Paginator),
                        ids: List[int] = Query(None)):
    response.headers["X-Total-Count"] = str(await channel.get_channels_count())
    return await channel.get_channels(skip=pagination.skip, limit=pagination.limit, ids=ids)


@router.get('/channels/{slug}', response_model=Channel, tags=['Каналы'], summary='Получить канал')
async def read_channel(db_channel: channels = Depends(find_channel)):
    return db_channel


@router.get('/channels/{slug}/videos',
            response_model=List[Video],
            tags=['Видео', 'Каналы'],
            summary='Получение списка видео канала')
async def read_channel_videos(pagination: Paginator = Depends(Paginator), db_channel: channels = Depends(find_channel)):
    return await video.get_videos(skip=pagination.skip, limit=pagination.limit, channel_id=db_channel['id'])
