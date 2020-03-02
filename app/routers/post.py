from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from app.db.session import Session
from app.models import User
from app.schemas.post import Post, CreatePost
from app.utils import get_db, get_current_admin
from app.crud import post

router = APIRouter()


@router.post('/posts/', response_model=Post, tags=['Посты'], summary='Добавление поста')
def create_post(new_post: CreatePost, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    if post.get_post_by_slug(db, new_post.slug):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Такой slug уже занят')
    db_post = post.create_post(db, new_post, admin)
    return db_post


@router.get('/posts/', response_model=List[Post], tags=['Посты'], summary='Получение списка постов')
def get_posts(skip: int = Query(0, ge=0), limit: int = Query(12, ge=0, le=50), db: Session = Depends(get_db)):
    return post.get_posts(db, skip, limit)


def find_post(slug: str, db: Session):
    db_post = post.get_post_by_slug(db, slug)
    if db_post:
        return db_post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Статья не найдена')
