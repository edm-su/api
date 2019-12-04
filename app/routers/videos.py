from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.utils import get_db

router = APIRouter()


@router.get('/videos/', response_model=schemas.VideoList, tags=['Видео'], summary='Получить список видео')
def read_videos(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    videos = crud.get_videos(db, skip, limit)
    count = crud.get_videos_count(db)
    return {'total_count': count, 'videos': videos}


@router.get('/videos/{slug}', response_model=schemas.Video, tags=['Видео'], summary='Получить видео')
def read_video(slug: str, db: Session = Depends(get_db)):
    video = crud.get_video(db, slug)
    if video:
        return video
    else:
        raise HTTPException(status_code=404, detail='Видео не найдено')
