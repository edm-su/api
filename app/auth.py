import typing
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from app.crud import user
from app.helpers import get_password_hash
from app.schemas.user import TokenData
from app.settings import settings

oauth_scheme = OAuth2PasswordBearer("/users/token", auto_error=False)


async def get_current_user(
    authorization: str | None = Header(None),
    token: str = Depends(oauth_scheme),
) -> typing.Mapping:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token and authorization:
        schema, _, token = authorization.partition(" ")
        token_length = 64
        if schema.lower() != "token" or len(token) != token_length:
            raise credentials_exception
        db_user = await user.get_user_by_token(token)
        if db_user is None:
            raise credentials_exception
        return db_user

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception  # noqa: TRY301
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    db_user = await user.get_user_by_username(token_data.username)
    if db_user is None:
        raise credentials_exception
    return db_user


async def get_current_user_or_guest(
    token: str = Depends(oauth_scheme),
) -> typing.Mapping | None:
    if token:
        return await get_current_user(token=token)
    return None


async def get_current_admin(
    db_user: dict = Depends(get_current_user),
) -> typing.Mapping:
    if not db_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь не является администратором",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db_user


async def authenticate_user(
    username: str,
    password: str,
) -> typing.Mapping | None:
    db_user = await user.get_user_by_username(username=username)
    if not db_user:
        return None
    if not verify_password(password, db_user["password"]):
        return None
    return db_user


def verify_password(password: str, hashed_password: str) -> bool:
    return get_password_hash(password) == hashed_password


def create_access_token(
    *,
    data: dict,
    expires_delta: timedelta = timedelta(days=31),
) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
