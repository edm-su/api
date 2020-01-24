from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import comment, video
from app.schemas.comment import Comment
from app.schemas.user import MyUser
from app.utils import get_db, get_current_user, get_current_admin

router = APIRouter()


@router.post('/videos/{video_slug}/comments/', response_model=Comment, tags=['Комментарии', 'Видео'],
             summary='Оставить комментарий')
def new_comment(video_slug: str,
                text: str,
                current_user: MyUser = Depends(get_current_user),
                db: Session = Depends(get_db)):
    if len(text) > 120:
        raise HTTPException(400, 'Максимальная длина сообщения 120 символов')
    if not text:
        raise HTTPException(400, 'Минимальная длина сообщения 1 символ')
    db_video = video.get_video_by_slug(db, video_slug)
    if db_video:
        db_comment = comment.create_comment(db, current_user, db_video, text)
        return db_comment
    else:
        raise HTTPException(status_code=404, detail='Видео не найдено')


@router.get('/videos/{video_slug}/comments/', response_model=List[Comment], tags=['Комментарии', 'Видео'],
            summary='Получить комментарии к видео')
def read_comments(video_slug: str, db: Session = Depends(get_db)):
    db_video = video.get_video_by_slug(db, video_slug)
    if db_video:
        return comment.get_comments_for_video(db_video)
    else:
        raise HTTPException(status_code=404, detail='Видео не найдено')


@router.get('/comments/', response_model=List[Comment], tags=['Комментарии'],
            summary='Получить список комментариев ко всем видео')
def comments_list(db: Session = Depends(get_db), admin: MyUser = Depends(get_current_admin), skip: int = 0,
                  limit: int = 50):
    return comment.get_comments(db, limit, skip)
