from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.utils import get_db

router = APIRouter()


@router.post('/users/', tags=['Пользователи'], summary='Регистрация пользователя', response_model=schemas.User)
def user_register(user: schemas.CreateUser, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(400, 'Такой email уже существует')
    if crud.get_user_by_nickname(db, user.nickname):
        raise HTTPException(400, 'Имя пользователя занято')
    return crud.create_user(db, user)
