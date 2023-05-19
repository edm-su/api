from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from starlette import status

from app.internal.controller.http.v1.dependencies.user import (
    create_get_user_by_username_usecase,
)
from app.internal.entity.settings import settings
from app.internal.entity.user import TokenData, User
from app.internal.usecase.exceptions.user import AuthError
from app.internal.usecase.user import GetUserByUsernameUseCase

oauth_scheme = OAuth2PasswordBearer("/users/signin", auto_error=False)


async def get_current_user(
    token: Annotated[
        str,
        Depends(oauth_scheme),
    ],
    usecase: Annotated[
        GetUserByUsernameUseCase,
        Depends(create_get_user_by_username_usecase),
    ],
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


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_admin(
    db_user: CurrentUser,
) -> User:
    if not db_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not admin",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db_user


CurrentAdmin = Annotated[User, Depends(get_current_admin)]
