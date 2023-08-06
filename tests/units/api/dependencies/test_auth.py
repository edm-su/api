from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.security import SecurityScopes
from typing_extensions import Self

from app.internal.controller.http.v1.dependencies.auth import (
    _check_scopes,
    get_current_admin,
    get_current_user,
    get_refresh_token_data,
)
from app.internal.controller.http.v1.dependencies.exceptions.auth import (
    TokenScopeError,
)
from app.internal.entity.user import RefreshTokenData, TokenData, User
from app.internal.usecase.exceptions.user import AuthError
from app.internal.usecase.user import (
    AbstractUserUseCase,
    GetUserByUsernameUseCase,
)


class TestAuthUser:
    @pytest.fixture()
    def token_data(
        self: Self,
        user: User,
    ) -> TokenData:
        return TokenData(
            sub=user.id,
            username=user.username,
            email=user.email,
        )

    @pytest.fixture()
    def usecase(
        self: Self,
        user: User,
    ) -> GetUserByUsernameUseCase:
        usecase = AsyncMock(repr=AbstractUserUseCase)
        usecase.execute.return_value = user
        return usecase

    async def test_get_current_user(
        self: Self,
        token_data: TokenData,
        usecase: AsyncMock,
        user: User,
    ) -> None:
        token = token_data.get_jwt_token()
        user = await get_current_user(token, usecase, SecurityScopes())

        usecase.execute.assert_awaited_once()
        assert user.id == token_data.sub

    async def test_get_current_user_bad_token(
        self: Self,
        usecase: GetUserByUsernameUseCase,
        token_data: TokenData,
    ) -> None:
        with pytest.raises(AuthError):
            await get_current_user("", usecase, SecurityScopes())

        token = token_data.get_jwt_token()
        with pytest.raises(AuthError):
            await get_current_user(token + "a", usecase, SecurityScopes())

    async def test_get_current_user_not_found(
        self: Self,
        usecase: AsyncMock,
        token_data: TokenData,
    ) -> None:
        token = token_data.get_jwt_token()
        usecase.execute.return_value = None
        with pytest.raises(AuthError):
            await get_current_user(token, usecase, SecurityScopes())


class TestAuthAdmin:
    async def test_get_current_admin(
        self: Self,
        user: User,
    ) -> None:
        user.is_admin = True
        assert await get_current_admin(user)

    async def test_get_current_admin_not_found(
        self: Self,
        user: User,
    ) -> None:
        with pytest.raises(HTTPException):
            await get_current_admin(user)


class TestSecurityScopes:
    async def test_check_scopes(
        self: Self,
    ) -> None:
        token_data = TokenData(
            sub=1,
            email="example@example.com",
            is_admin=True,
            scope=["user:refresh"],
            token_id=1,
            username="username",
        )

        _check_scopes(
            SecurityScopes(["user:refresh"]),
            token_data,
        )

    async def test_check_scopes_error(
        self: Self,
    ) -> None:
        token_data = TokenData(
            sub=1,
            email="example@example.com",
            is_admin=True,
            scope=[],
            token_id=1,
            username="username",
        )

        with pytest.raises(TokenScopeError):
            _check_scopes(
                SecurityScopes(["user:refresh"]),
                token_data,
            )


class TestRefreshTokenData:
    @pytest.fixture()
    def refresh_token(
        self: Self,
    ) -> RefreshTokenData:
        return RefreshTokenData(
            email="example@example.com",
            is_admin=True,
            scope=["user:refresh"],
            sub=1,
            username="username",
        )

    @pytest.fixture()
    def usecase(
        self: Self,
    ) -> GetUserByUsernameUseCase:
        return AsyncMock(repr=GetUserByUsernameUseCase)

    async def test_get_refresh_token_data(
        self: Self,
        refresh_token: RefreshTokenData,
        usecase: GetUserByUsernameUseCase,
    ) -> None:
        assert await get_refresh_token_data(
            refresh_token.get_jwt_token(),
            usecase,
        )

    async def test_get_refresh_token_data_bad_token(
        self: Self,
        refresh_token: RefreshTokenData,
        usecase: GetUserByUsernameUseCase,
    ) -> None:
        with pytest.raises(AuthError):
            await get_refresh_token_data(
                refresh_token.get_jwt_token() + "a",
                usecase,
            )

    async def test_no_scope_error(
        self: Self,
        refresh_token: RefreshTokenData,
        usecase: GetUserByUsernameUseCase,
    ) -> None:
        refresh_token.scope = []
        with pytest.raises(TokenScopeError):
            await get_refresh_token_data(
                refresh_token.get_jwt_token(),
                usecase,
            )
