from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from starlette import status

from app.helpers import get_password_hash
from app.internal.controller.http.v1.depencies.user import (
    create_get_user_by_username_usecase,
)
from app.internal.entity.user import TokenData, User
from app.internal.usecase.exceptions.user import AuthError
from app.internal.usecase.user import GetUserByUsernameUseCase
from app.settings import settings

oauth_scheme = OAuth2PasswordBearer("/users/signin", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth_scheme),
    usecase: GetUserByUsernameUseCase = Depends(
        create_get_user_by_username_usecase,
    ),
) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
        )
        token_data = TokenData.parse_obj(payload)
    except jwt.PyJWTError as e:
        raise AuthError from e
    except ValidationError as e:
        raise AuthError from e
    db_user = await usecase.execute(token_data.username)
    if db_user is None:
        raise AuthError
    return db_user


async def get_current_user_or_guest(
    token: str = Depends(oauth_scheme),
) -> User | None:
    if token:
        return await get_current_user(token=token)
    return None


async def get_current_admin(
    db_user: User = Depends(get_current_user),
) -> User:
    if not db_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь не является администратором",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db_user


def verify_password(password: str, hashed_password: str) -> bool:
    return get_password_hash(password) == hashed_password


def create_token(
    *,
    data: TokenData,
    expires_delta: timedelta = timedelta(days=31),
) -> str:
    to_encode = data.dict()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
