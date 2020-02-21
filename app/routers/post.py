from fastapi import APIRouter, Depends, HTTPException

from app.db.session import Session
from app.models import User
from app.schemas.post import Post, CreatePost
from app.utils import get_db, get_current_admin
from app.crud import post

router = APIRouter()


@router.post('/posts/', response_model=Post, tags=['Посты'], summary='Добавление поста')
def create_post(new_post: CreatePost, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    if post.get_post_by_slug(db, new_post.slug):
        raise HTTPException(422, 'Такой slug уже занят')
    db_post = post.create_post(db, new_post, admin)
    return db_post
