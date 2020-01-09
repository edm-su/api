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
        nickname: str = payload.get('sub')
        if nickname is None:
            raise credentials_exception
        token_data = schemas.TokenData(nickname=nickname)
    except PyJWTError:
        raise credentials_exception
    user = crud.get_user_by_nickname(db, token_data.nickname)
    if user is None:
        raise credentials_exception
    return user


def authenticate_user(nickname: str, password: str, db: Session):
    user = crud.get_user_by_nickname(db, nickname)
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
