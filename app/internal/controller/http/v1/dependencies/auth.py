from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Query, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pydantic import ValidationError
from starlette import status

from app.internal.controller.http.v1.dependencies.exceptions.auth import (
    TokenScopeError,
)
from app.internal.controller.http.v1.dependencies.user import (
    create_get_user_by_username_usecase,
)
from app.internal.entity.settings import settings
from app.internal.entity.user import TokenData, User
from app.internal.usecase.exceptions.user import AuthError
from app.internal.usecase.user import GetUserByUsernameUseCase

scopes = {
    "user:change_password": "Change your password",
    "user:activate": "Activate your account",
    "user:refresh": "Refresh your access token",
}
oauth_scheme = OAuth2PasswordBearer(
    "/users/sign-in",
    auto_error=False,
    scopes=scopes,
)


async def get_current_user(
    token: Annotated[
        str,
        Depends(oauth_scheme),
    ],
    usecase: Annotated[
        GetUserByUsernameUseCase,
        Depends(create_get_user_by_username_usecase),
    ],
    security_scopes: SecurityScopes,
) -> User:
    token_data, db_user = await _authorize_user(token, usecase)
    _check_scopes(security_scopes, token_data)
    return db_user


def _check_scopes(
    security_scopes: SecurityScopes,
    token_data: TokenData,
) -> None:
    for scope in security_scopes.scopes:
        if scope not in token_data.scope:
            raise TokenScopeError(security_scopes.scope_str)


async def _authorize_user(
    token: str,
    usecase: GetUserByUsernameUseCase,
) -> tuple[TokenData, User]:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
        )
        token_data = TokenData.model_validate(payload)
    except (jwt.PyJWTError, ValidationError) as e:
        raise AuthError from e
    db_user = await usecase.execute(token_data.username)
    if db_user is None:
        raise AuthError
    return token_data, db_user


async def get_refresh_token_data_and_user(
    refresh_token: Annotated[str, Query],
    usecase: Annotated[
        GetUserByUsernameUseCase,
        Depends(create_get_user_by_username_usecase),
    ],
) -> TokenData:
    token_data, _ = await _authorize_user(refresh_token, usecase)
    _check_scopes(
        SecurityScopes(["user:refresh"]),
        token_data,
    )
    return token_data


CurrentUser = Annotated[User, Security(get_current_user)]


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
