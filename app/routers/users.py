from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.crud import user
from app.schemas.user import CreateUser, MyUser, Token, UserRecovery, ChangePassword, UserPassword, User
from app.utils import get_db, authenticate_user, create_access_token, get_current_user, get_password_hash
from tasks import send_recovery_email

router = APIRouter()


@router.post('/users/', tags=['Пользователи'], summary='Регистрация пользователя', response_model=MyUser)
def user_register(db_user: CreateUser, db: Session = Depends(get_db)):
    if user.get_user_by_email(db, db_user.email):
        raise HTTPException(400, 'Такой email уже существует')
    if user.get_user_by_username(db, db_user.username):
        raise HTTPException(400, 'Имя пользователя занято')
    return user.create_user(db, db_user)


@router.post('/users/activate', tags=['Пользователи'], summary='Активация учётной записи', status_code=204)
def user_activate(code: str = Query(..., regex=r'^[A-Z\d]{10}$'), db: Session = Depends(get_db)):
    db_user = user.activate_user(db, code)
    if db_user:
        return {}
    else:
        raise HTTPException(400, 'Неверный код или учётная запись уже активирована')


@router.post('/users/token', response_model=Token, tags=['Пользователи'],
             summary='Авторизация и получение токена')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = authenticate_user(form_data.username, form_data.password, db)
    if not db_user:
        raise HTTPException(401, 'Неверное имя пользователя или пароль', headers={'WWW-Authenticate': 'Bearer'})
    if not db_user.is_active:
        raise HTTPException(401, 'Учётная запись не подтверждена', headers={'WWW-Authenticate': 'Bearer'})
    if db_user.is_banned:
        raise HTTPException(401, 'Учётная запись заблокирована', headers={'WWW-Authenticate': 'Bearer'})
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={'sub': db_user.username}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/users/me', response_model=MyUser, tags=['Пользователи'], summary='Получение данных пользователя')
async def read_current_user(current_user: MyUser = Depends(get_current_user)):
    return current_user


@router.post('/users/password', tags=['Пользователи'], summary='Восстановаление пароля')
async def user_recovery(email: UserRecovery, db: Session = Depends(get_db)):
    db_user = user.get_user_by_email(db, email.email)
    if not db_user:
        raise HTTPException(400, 'Пользователь с таким email не найден')
    code = user.generate_recovery_user_code(db, db_user)
    send_recovery_email.delay(db_user.email, code)
    return {'Выслано письмо с инструкцией для смены пароля'}


@router.put('/users/password', tags=['Пользователи'], summary='Изменение пароля', status_code=204)
async def change_password(password: ChangePassword, current_user: MyUser = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if get_password_hash(password.old_password) == current_user.password:
        user.change_password(db, current_user, password.password)
        return {}
    else:
        raise HTTPException(400, 'Старый пароль неверный')


@router.put('/users/password/{code}', tags=['Пользователи'], summary='Завершение восстановления пароля',
            status_code=204)
async def complete_recovery(code: str, password: UserPassword, db: Session = Depends(get_db)):
    db_user = user.get_user_by_recovery_code(db, code)
    if db_user:
        user.change_password(db, db_user, password.password, True)
        return {}
    else:
        raise HTTPException(400, 'Неверный код или истёк срок действия')


@router.get('/users/{_id}', response_model=User, tags=['Пользователи'],
            summary='Получение информации о пользователе')
async def read_user(_id: int, db: Session = Depends(get_db)):
    db_user = user.get_user_by_id(db, _id)
    if db_user:
        return db_user
    else:
        raise HTTPException(404, 'Пользователь не найден')
