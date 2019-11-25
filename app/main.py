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


@app.get('/events/', response_model=List[schemas.Event], tags=['События'], summary='Получить список событий')
def read_events(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    events = crud.get_events(db, skip=skip, limit=limit)
    return events
