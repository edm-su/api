from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, crud
from app.database import SessionLocal

app = FastAPI()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get('/channels/', response_model=List[schemas.Channel], tags=['Каналы'], summary='Получить список каналов')
def read_channels(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    channels = crud.get_channels(db, skip=skip, limit=limit)
    return channels


@app.get('/channels/{slug}', response_model=schemas.Channel, tags=['Каналы'], summary='Получить канал')
def read_channel(slug: str, db: Session = Depends(get_db)):
    channel = crud.get_channel(db, slug)
    if channel:
        return channel
    else:
        raise HTTPException(status_code=404, detail='Канал не найден')


@app.get('/channels/{slug}/videos',
         response_model=List[schemas.Video],
         tags=['Видео', 'События'],
         summary='Получение видео события')
def read_channel_videos(slug: str, limit: int = 25, skip: int = 0, db: Session = Depends(get_db)):
    channel = crud.get_channel(db, slug)
    if channel:
        return crud.get_videos(db, skip, limit, channel)
    else:
        raise HTTPException(status_code=404, detail='Канал не найден')


@app.get('/events/', response_model=List[schemas.Event], tags=['События'], summary='Получить список событий')
def read_events(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    events = crud.get_events(db, skip=skip, limit=limit)
    return events


@app.get('/events/{slug}', response_model=schemas.Event, tags=['События'], summary='Получить событие')
def read_event(slug: str, db: Session = Depends(get_db)):
    event = crud.get_event(db, slug)
    if event:
        return event
    else:
        raise HTTPException(status_code=404, detail='Событие не найдено')


@app.get('/djs/', response_model=List[schemas.Dj], tags=['DJs'], summary='Получить список диджеев')
def read_djs(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    djs = crud.get_djs(db, skip, limit)
    return djs


@app.get('/djs/{slug}', response_model=schemas.Dj, tags=['DJs'], summary='Получить диджея')
def read_dj(slug: str, db: Session = Depends(get_db)):
    dj = crud.get_dj(db, slug)
    if dj:
        return dj
    else:
        raise HTTPException(status_code=404, detail='Диджей не найден')


@app.get('/videos/', response_model=List[schemas.Video], tags=['Видео'], summary='Получить список видео')
def read_videos(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    videos = crud.get_videos(db, skip, limit)
    return videos


@app.get('/videos/{slug}', response_model=schemas.Video, tags=['Видео'], summary='Получить видео')
def read_video(slug: str, db: Session = Depends(get_db)):
    video = crud.get_video(db, slug)
    if video:
        return video
    else:
        raise HTTPException(status_code=404, detail='Видео не найдено')
