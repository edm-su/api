from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.crud import event, video
from app.schemas.event import Event
from app.schemas.video import Video
from app.utils import get_db

router = APIRouter()


@router.get('/events/', response_model=List[Event], tags=['События'], summary='Получить список событий')
def read_events(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    events = event.get_events(db, skip=skip, limit=limit)
    return events


@router.get('/events/{slug}', response_model=Event, tags=['События'], summary='Получить событие')
def read_event(slug: str, db: Session = Depends(get_db)):
    db_event = event.get_event(db, slug)
    if db_event:
        return db_event
    else:
        raise HTTPException(status_code=404, detail='Событие не найдено')


@router.get('/events/{slug}/videos',
            response_model=List[Video],
            tags=['Видео', 'События'],
            summary='Получение списка видео для события')
def read_event_videos(slug: str, limit: int = 25, skip: int = 0, db: Session = Depends(get_db)):
    db_event = event.get_event(db, slug)
    if db_event:
        return video.get_videos(db, skip, limit, db_event)
    else:
        raise HTTPException(status_code=404, detail='Событие не найдено')
