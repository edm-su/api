import typing
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from starlette import status

from app import settings
from app.crud import user
from app.helpers import get_password_hash
from app.schemas.user import TokenData

oauth_scheme = OAuth2PasswordBearer('/users/token', auto_error=False)


async def get_current_user(
        token: str = Depends(oauth_scheme),
) -> typing.Mapping:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Не удалось проверить учётные данные',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    db_user = await user.get_user_by_username(token_data.username)
    if db_user is None:
        raise credentials_exception
    return db_user


async def get_current_user_or_guest(
        token: str = Depends(oauth_scheme),
) -> typing.Optional[typing.Mapping]:
    if token:
        db_user = await get_current_user(token=token)
        return db_user


async def get_current_admin(
        db_user: dict = Depends(get_current_user),
) -> typing.Mapping:
    if not db_user['is_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Пользователь не является администратором',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return db_user


async def authenticate_user(
        username: str,
        password: str,
) -> typing.Union[typing.Mapping, bool]:
    db_user = await user.get_user_by_username(username=username)
    if not db_user:
        return False
    if not verify_password(password, db_user['password']):
        return False
    return db_user


def verify_password(password, hashed_password) -> bool:
    return get_password_hash(password) == hashed_password


def create_access_token(
        *,
        data: dict,
        expires_delta: timedelta = timedelta(days=31),
) -> bytes:
    to_encode = data.copy()
    to_encode.update({'exp': datetime.utcnow() + expires_delta})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm='HS256')
    return encoded_jwt
