from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.utils import get_db, get_current_admin

router = APIRouter()


@router.get('/videos/', response_model=schemas.VideoList, tags=['Видео'], summary='Получить список видео')
def read_videos(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    videos = crud.get_videos(db, skip, limit)
    count = crud.get_videos_count(db)
    return {'total_count': count, 'videos': videos}


@router.get('/videos/{slug}', response_model=schemas.Video, tags=['Видео'], summary='Получить видео')
def read_video(slug: str, db: Session = Depends(get_db)):
    video = find_video(slug, db)
    return video


@router.delete('/videos/{slug}', tags=['Видео'], summary='Удаление видео', status_code=204)
def delete_video(slug: str, db: Session = Depends(get_db), admin: schemas.MyUser = Depends(get_current_admin)):
    video = find_video(slug, db)
    if crud.delete_video(db, video):
        return {}
    else:
        raise HTTPException(400, 'При удалении произошла ошибка')


@router.get('/videos/{slug}/related', response_model=List[schemas.Video], tags=['Видео'],
            summary='Получить похожие видео')
def read_related_videos(slug: str, db: Session = Depends(get_db), limit: int = 15):
    video = find_video(slug, db)
    related_videos = crud.get_related_videos(video.title, db, limit)
    return related_videos


def find_video(slug: str, db: Session):
    video = crud.get_video_by_slug(db, slug)
    if video:
        return video
    else:
        raise HTTPException(status_code=404, detail='Видео не найдено')
