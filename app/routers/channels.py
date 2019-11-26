from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.utils import get_db

router = APIRouter()


@router.get('/channels/', response_model=List[schemas.Channel], tags=['Каналы'], summary='Получить список каналов')
def read_channels(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    channels = crud.get_channels(db, skip=skip, limit=limit)
    return channels


@router.get('/channels/{slug}', response_model=schemas.Channel, tags=['Каналы'], summary='Получить канал')
def read_channel(slug: str, db: Session = Depends(get_db)):
    channel = crud.get_channel(db, slug)
    if channel:
        return channel
    else:
        raise HTTPException(status_code=404, detail='Канал не найден')


@router.get('/channels/{slug}/videos',
            response_model=List[schemas.Video],
            tags=['Видео', 'Каналы'],
            summary='Получение списка видео для канала')
def read_channel_videos(slug: str, limit: int = 25, skip: int = 0, db: Session = Depends(get_db)):
    channel = crud.get_channel(db, slug)
    if channel:
        return crud.get_videos(db, skip, limit, channel)
    else:
        raise HTTPException(status_code=404, detail='Канал не найден')
