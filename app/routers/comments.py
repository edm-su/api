from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.utils import get_db, get_current_user
from app import schemas, crud

router = APIRouter()


@router.post('/videos/{video_slug}/comments/', response_model=schemas.Comment, tags=['Комментарии', 'Видео'],
             summary='Оставить комментарий')
def new_comment(video_slug: str,
                text: str,
                current_user: schemas.User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    video = crud.get_video_by_slug(db, video_slug)
    if video:
        comment = crud.create_comment(db, current_user, video, text)
        return comment
    else:
        raise HTTPException(status_code=404, detail='Видео не найдено')


@router.get('/videos/{video_slug}/comments/', response_model=List[schemas.Comment], tags=['Комментарии', 'Видео'],
            summary='Получить комментарии к видео')
def get_comments(video_slug: str, db: Session = Depends(get_db)):
    video = crud.get_video_by_slug(db, video_slug)
    if video:
        return crud.get_comments(db, video)
    else:
        raise HTTPException(status_code=404, detail='Видео не найдено')
