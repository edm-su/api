from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from typing_extensions import Self

from edm_su_api.internal.controller.http.v1.dependencies.livestream import (
    find_livestream,
)
from edm_su_api.internal.usecase.exceptions.livestream import (
    LiveStreamNotFoundError,
)
from edm_su_api.internal.usecase.livestream import GetLiveStreamUseCase

pytestmark = pytest.mark.anyio


class TestFindLiveStream:
    async def test_find_livestream(
        self: Self,
    ) -> None:
        usecase = AsyncMock(repr=GetLiveStreamUseCase)
        assert await find_livestream(
            1,
            usecase,
        )

    async def test_not_found(
        self: Self,
    ) -> None:
        usecase = AsyncMock(repr=GetLiveStreamUseCase)
        usecase.execute.side_effect = LiveStreamNotFoundError
        with pytest.raises(HTTPException):
            await find_livestream(
                1,
                usecase,
            )
