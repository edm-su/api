from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.crud import channel, video
from app.schemas.channel import Channel
from app.schemas.video import Video
from app.utils import get_db

router = APIRouter()


@router.get('/channels/', response_model=List[Channel], tags=['Каналы'], summary='Получить список каналов')
def read_channels(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    channels = channel.get_channels(db, skip=skip, limit=limit)
    return channels


@router.get('/channels/{slug}', response_model=Channel, tags=['Каналы'], summary='Получить канал')
def read_channel(slug: str, db: Session = Depends(get_db)):
    db_channel = channel.get_channel(db, slug)
    if db_channel:
        return db_channel
    else:
        raise HTTPException(status_code=404, detail='Канал не найден')


@router.get('/channels/{slug}/videos',
            response_model=List[Video],
            tags=['Видео', 'Каналы'],
            summary='Получение списка видео для канала')
def read_channel_videos(slug: str, limit: int = 25, skip: int = 0, db: Session = Depends(get_db)):
    db_channel = channel.get_channel(db, slug)
    if db_channel:
        return video.get_videos(db, skip, limit, db_channel)
    else:
        raise HTTPException(status_code=404, detail='Канал не найден')
