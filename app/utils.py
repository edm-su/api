import hashlib
import string
from datetime import datetime, timedelta
import random

import jwt
from fastapi import Depends, HTTPException
from jwt import PyJWTError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer

from app import settings, schemas, crud
from app.settings import SECRET_KEY


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


oauth_scheme = OAuth2PasswordBearer('/users/token')


def get_password_hash(password):
    return hashlib.sha256(f'{password}{settings.SECRET_KEY}'.encode()).hexdigest()


def verify_password(password, hashed_password):
    return get_password_hash(password) == hashed_password


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth_scheme)):
    credentials_exception = HTTPException(401, 'Не удалось проверить учётные данные', {'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(db: Session = Depends(get_db), user: schemas.MyUser = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(401, 'Пользователь не является администратором', {'WWW-Authenticate': 'Bearer'})
    return user


def authenticate_user(username: str, password: str, db: Session):
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm='HS256')
    return encoded_jwt


def generate_secret_code(n: int = 10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))
