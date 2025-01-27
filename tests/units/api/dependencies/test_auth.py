import pytest
from fastapi import HTTPException, status
from typing_extensions import Self

from edm_su_api.internal.controller.http.v1.dependencies.auth import (
    get_current_user,
    get_optional_user,
)
from edm_su_api.internal.entity.user import User

pytestmark = pytest.mark.anyio


class TestGetCurrentUser:
    async def test_get_current_user(
        self: Self,
    ) -> None:
        user = await get_current_user(x_user="test_user")
        assert isinstance(user, User)
        assert user.id == "test_user"

    async def test_unauthorized(
        self: Self,
    ) -> None:
        with pytest.raises(HTTPException) as exc_info:
            _ = await get_current_user(x_user=None)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetOptionalUser:
    async def test_get_optional_user(
        self: Self,
    ) -> None:
        user = await get_optional_user(x_user="test_user")
        assert isinstance(user, User)
        assert user.id == "test_user"

    async def test_anonymous(
        self: Self,
    ) -> None:
        user = await get_optional_user(x_user="Anonymous")
        assert user is None

    async def test_no_user(
        self: Self,
    ) -> None:
        user = await get_optional_user(x_user=None)
        assert user is None

    async def test_case_insensitive_anonymous(
        self: Self,
    ) -> None:
        user = await get_optional_user("anonymous")
        assert user is None
