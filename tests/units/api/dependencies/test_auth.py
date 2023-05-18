from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from typing_extensions import Self

from app.internal.controller.http.v1.dependencies.auth import (
    get_current_admin,
    get_current_user,
)
from app.internal.entity.user import TokenData, User
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
            id=user.id,
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
        user = await get_current_user(token, usecase)

        usecase.execute.assert_awaited_once()
        assert user.id == token_data.id

    async def test_get_current_user_bad_token(
        self: Self,
        usecase: GetUserByUsernameUseCase,
        token_data: TokenData,
    ) -> None:
        with pytest.raises(AuthError):
            await get_current_user("", usecase)

        token = token_data.get_jwt_token()
        with pytest.raises(AuthError):
            await get_current_user(token + "a", usecase)

    async def test_get_current_user_not_found(
        self: Self,
        usecase: AsyncMock,
        token_data: TokenData,
    ) -> None:
        token = token_data.get_jwt_token()
        usecase.execute.return_value = None
        with pytest.raises(AuthError):
            await get_current_user(token, usecase)


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
