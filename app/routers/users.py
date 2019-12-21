from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, schemas
from app.utils import get_db, authenticate_user, create_access_token, get_current_user
from tasks import send_recovery_email

router = APIRouter()


@router.post('/users/', tags=['Пользователи'], summary='Регистрация пользователя', response_model=schemas.User)
def user_register(user: schemas.CreateUser, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(400, 'Такой email уже существует')
    if crud.get_user_by_nickname(db, user.nickname):
        raise HTTPException(400, 'Имя пользователя занято')
    return crud.create_user(db, user)


@router.post('/users/activate', tags=['Пользователи'], summary='Активация учётной записи', status_code=204)
def user_activate(code: str = Query(..., regex='^[A-Z\d]{10}$'), db: Session = Depends(get_db)):
    user = crud.activate_user(db, code)
    if user:
        return {}
    else:
        raise HTTPException(400, 'Неверный код или учётная запись уже активирована')


@router.post('/users/token', response_model=schemas.Token, tags=['Пользователи'],
             summary='Авторизация и получение токена')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(401, 'Неверное имя пользователя или пароль', headers={'WWW-Authenticate': 'Bearer'})
    if not user.is_active:
        raise HTTPException(401, 'Учётная запись не подтверждена', headers={'WWW-Authenticate': 'Bearer'})
    if user.is_banned:
        raise HTTPException(401, 'Учётная запись заблокирована', headers={'WWW-Authenticate': 'Bearer'})
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={'sub': user.nickname}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/users/me', response_model=schemas.User, tags=['Пользователи'], summary='Получение данных пользователя')
async def read_current_user(current_user: schemas.User = Depends(get_current_user)):
    return current_user


@router.post('/users/password', tags=['Пользователи'], summary='Восстановаление пароля')
async def user_recovery(email: schemas.UserRecovery, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email.email)
    if not user:
        raise HTTPException(400, 'Пользователь с таким email не найден')
    code = crud.generate_recovery_user_code(db, user)
    send_recovery_email.delay(user.email, code)
    return {'Выслано письмо с инструкцией для смены пароля'}


@router.put('/users/password', tags=['Пользователи'], summary='Изменение пароля', status_code=204)
async def change_password(password: schemas.ChangePassword, current_user: schemas.User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if crud.get_password_hash(password.old_password) == current_user.password:
        crud.change_password(db, current_user, password.password)
        return {}
    else:
        raise HTTPException(400, 'Старый пароль неверный')


@router.put('/users/password/{code}', tags=['Пользователи'], summary='Завершение восстановления пароля',
            status_code=204)
async def complete_recovery(code: str, password: schemas.UserPassword, db: Session = Depends(get_db)):
    user = crud.get_user_by_recovery_code(db, code)
    if user:
        crud.change_password(db, user, password.password, True)
        return {}
    else:
        raise HTTPException(400, 'Неверный код или истёк срок действия')
