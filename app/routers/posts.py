import re
import typing
from typing import List

from asyncpg import UniqueViolationError
from fastapi import APIRouter, Depends, HTTPException, Response
from starlette import status

from app.auth import get_current_admin
from app.crud import post
from app.db import users
from app.helpers import Paginator
from app.schemas.post import Post, CreatePost

router = APIRouter()


async def find_post(slug: str) -> typing.Mapping:
    db_post = await post.get_post_by_slug(slug=slug)
    if db_post:
        return db_post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пост не найден')


@router.post('/posts/', response_model=Post, tags=['Посты'], summary='Добавление поста')
async def create_post(new_post: CreatePost, admin: dict = Depends(get_current_admin)):
    try:
        return await post.create_post(post=new_post, user_id=admin['id'])
    except UniqueViolationError as e:
        message = re.findall(r'posts_([a-zA-Z]+)_key', e.message)[0]
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f'Запись с таким значением {message} уже существует')


@router.get('/posts/', response_model=List[Post], tags=['Посты'], summary='Получение списка постов')
async def get_posts(response: Response, paginate: Paginator = Depends(Paginator)):
    response.headers['X-Total-Count'] = str(await post.get_posts_count())
    return await post.get_posts(skip=paginate.skip, limit=paginate.limit)


@router.get('/posts/{slug}', response_model=Post, tags=['Посты'], summary='Получить пост')
async def get_post(db_post: dict = Depends(find_post)):
    return db_post


@router.delete('/posts/{slug}', tags=['Посты'], summary='Удалить пост', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(slug: str, admin: users = Depends(get_current_admin)):
    if await post.delete_post(slug=slug):
        return {}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пост не найден')
