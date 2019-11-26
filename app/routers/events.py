from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.utils import get_db

router = APIRouter()


@router.get('/events/', response_model=List[schemas.Event], tags=['События'], summary='Получить список событий')
def read_events(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    events = crud.get_events(db, skip=skip, limit=limit)
    return events


@router.get('/events/{slug}', response_model=schemas.Event, tags=['События'], summary='Получить событие')
def read_event(slug: str, db: Session = Depends(get_db)):
    event = crud.get_event(db, slug)
    if event:
        return event
    else:
        raise HTTPException(status_code=404, detail='Событие не найдено')


@router.get('/events/{slug}/videos',
            response_model=List[schemas.Video],
            tags=['Видео', 'События'],
            summary='Получение списка видео для события')
def read_event_videos(slug: str, limit: int = 25, skip: int = 0, db: Session = Depends(get_db)):
    event = crud.get_event(db, slug)
    if event:
        return crud.get_videos(db, skip, limit, event)
    else:
        raise HTTPException(status_code=404, detail='Событие не найдено')
