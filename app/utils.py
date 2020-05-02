import hashlib
import random
import string
from datetime import datetime, timedelta

import boto3
import jwt
from algoliasearch.search_client import SearchClient
from fastapi import Depends, HTTPException
from jwt import PyJWTError
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request

from app import settings
from app.schemas.user import MyUser, TokenData
from app.crud import user


def get_db(request: Request):
    return request.state.db


oauth_scheme = OAuth2PasswordBearer('/users/token', auto_error=False)


def verify_password(password, hashed_password):
    return get_password_hash(password) == hashed_password


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth_scheme)):
    credentials_exception = HTTPException(401, 'Не удалось проверить учётные данные', {'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    db_user = user.get_user_by_username(db, token_data.username)
    if db_user is None:
        raise credentials_exception
    return db_user


async def get_current_user_or_guest(db: Session = Depends(get_db), token: str = Depends(oauth_scheme)):
    if token:
        db_user = await get_current_user(db, token)
        return db_user


async def get_current_admin(db: Session = Depends(get_db), db_user: MyUser = Depends(get_current_user)):
    if not db_user.is_admin:
        raise HTTPException(401, 'Пользователь не является администратором', {'WWW-Authenticate': 'Bearer'})
    return db_user


def authenticate_user(username: str, password: str, db: Session):
    db_user = user.get_user_by_username(db, username)
    if not db_user:
        return False
    if not verify_password(password, db_user.password):
        return False
    return db_user


def create_access_token(*, data: dict, expires_delta: timedelta = timedelta(days=31)):
    to_encode = data.copy()
    to_encode.update({'exp': datetime.utcnow() + expires_delta})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm='HS256')
    return encoded_jwt


def algolia_client():
    client = SearchClient.create(settings.ALGOLIA_APP_ID, settings.ALGOLIA_API_KEY)
    index = client.init_index(settings.ALGOLIA_INDEX)
    return index


def s3_client():
    s3 = boto3.client('s3', endpoint_url=settings.S3_ENDPOINT, aws_secret_access_key=settings.S3_ACCESS_KEY,
                      aws_access_key_id=settings.S3_ACCESS_KEY_ID)
    return s3


def get_password_hash(password):
    return hashlib.sha256(f'{password}{settings.SECRET_KEY}'.encode()).hexdigest()


def generate_secret_code(n: int = 10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))
