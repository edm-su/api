from typing import List, Mapping

from fastapi import APIRouter, HTTPException, Depends, Response, Query
from starlette import status

from app.auth import get_current_admin
from app.crud import channel, video
from app.helpers import Paginator
from app.schemas.channel import Channel
from app.schemas.video import Video

router = APIRouter()


async def find_channel(slug: str) -> Mapping:
    db_channel = await channel.get_channel_by_slug(slug=slug)
    if db_channel is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Канал не найден')
    return db_channel


@router.get(
    '/channels/',
    response_model=List[Channel],
    tags=['Каналы'],
    summary='Получить список каналов',
)
async def read_channels(
        response: Response,
        pagination: Paginator = Depends(Paginator),
        ids: List[int] = Query(None),
) -> List[Mapping]:
    response.headers["X-Total-Count"] = str(await channel.get_channels_count())
    return await channel.get_channels(pagination.skip, pagination.limit, ids)


@router.get(
    '/channels/{slug}',
    response_model=Channel,
    tags=['Каналы'],
    summary='Получить канал',
)
async def read_channel(db_channel: Mapping = Depends(find_channel)) -> Mapping:
    return db_channel


@router.get(
    '/channels/{slug}/videos',
    response_model=List[Video],
    tags=['Видео', 'Каналы'],
    summary='Получение списка видео канала',
)
async def read_channel_videos(
        pagination: Paginator = Depends(Paginator),
        db_channel: Mapping = Depends(find_channel),
) -> List[Mapping]:
    return await video.get_videos(
        pagination.skip,
        pagination.limit,
        db_channel['id'],
    )


@router.delete(
    '/channels/{slug}',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['Каналы'],
    summary='Удаление канала',
)
async def delete_channel(
        db_channel: Mapping = Depends(find_channel),
        admin: Mapping = Depends(get_current_admin),
) -> None:
    await channel.delete_channel(db_channel['id'])
