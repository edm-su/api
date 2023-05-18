from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from typing_extensions import Self

from app.internal.controller.http.v1.dependencies.post import find_post
from app.internal.usecase.exceptions.post import PostNotFoundError
from app.internal.usecase.post import GetPostBySlugUseCase


class TestFindPost:
    async def test_find_post(
        self: Self,
    ) -> None:
        usecase = AsyncMock(repr=GetPostBySlugUseCase)
        assert await find_post(
            "test",
            usecase,
        )

    async def test_not_found(
        self: Self,
    ) -> None:
        usecase = AsyncMock(repr=GetPostBySlugUseCase)
        usecase.execute.side_effect = PostNotFoundError
        with pytest.raises(HTTPException):
            await find_post(
                "test",
                usecase,
            )
