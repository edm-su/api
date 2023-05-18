from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from typing_extensions import Self

from app.internal.controller.http.v1.dependencies.video import find_video
from app.internal.usecase.exceptions.video import VideoNotFoundError
from app.internal.usecase.video import GetVideoBySlugUseCase


class TestFindVideo:
    async def test_find_video(
        self: Self,
    ) -> None:
        usecase = AsyncMock(repr=GetVideoBySlugUseCase)

        assert await find_video("test", usecase)
        usecase.execute.assert_awaited_once()

    async def test_not_found(
        self: Self,
    ) -> None:
        usecase = AsyncMock(repr=GetVideoBySlugUseCase)
        usecase.execute.side_effect = VideoNotFoundError

        with pytest.raises(HTTPException):
            await find_video("test", usecase)
        usecase.execute.assert_awaited_once()
