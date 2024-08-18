import io
from typing import IO
from unittest.mock import AsyncMock

import pytest
from pytest_httpx import HTTPXMock
from typing_extensions import Self

from edm_su_api.internal.entity.settings import settings
from edm_su_api.internal.entity.upload import ImageURL
from edm_su_api.internal.usecase.exceptions.upload import (
    FileIsNotImageError,
    FileIsTooLargeError,
)
from edm_su_api.internal.usecase.repository.upload import (
    AbstractUploadRepository,
)
from edm_su_api.internal.usecase.upload import (
    UploadImageURLUseCase,
    UploadImageUseCase,
)


@pytest.fixture
def repository() -> AbstractUploadRepository:
    return AsyncMock(repr=AbstractUploadRepository)


class TestUploadImageUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        settings.static_url = "https://test.local"
        repository.upload.return_value = None

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
        image: IO[bytes],
    ) -> UploadImageUseCase:
        return UploadImageUseCase(repository, image)

    async def test_upload_image(
        self: Self,
        usecase: AsyncMock,
        repository: AsyncMock,
    ) -> None:
        await usecase.execute()

        repository.upload.assert_awaited_once()

    async def test_max_upload_size(
        self: Self,
        repository: AbstractUploadRepository,
    ) -> None:
        buffer_size = 5 * 1024 * 1024 + 1
        buffer = io.BytesIO(b"\x00" * buffer_size)

        usecase = UploadImageUseCase(repository, buffer)
        with pytest.raises(FileIsTooLargeError):
            await usecase.execute()


class TestUploadImageURLUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        settings.static_url = "https://test.local"
        repository.upload.return_value = None

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> UploadImageURLUseCase:
        return UploadImageURLUseCase(
            repository,
            ImageURL(url="http://test.local/test.jpeg"),
        )

    async def test_upload_image_url(
        self: Self,
        httpx_mock: HTTPXMock,
        usecase: AsyncMock,
        repository: AsyncMock,
        image: IO[bytes],
    ) -> None:
        httpx_mock.add_response(
            method="HEAD",
            url="http://test.local/test.jpeg",
            headers={"Content-Type": "image/jpeg", "Content-Length": "123"},
        )
        image.seek(0)
        content = image.read()
        httpx_mock.add_response(
            method="GET",
            url="http://test.local/test.jpeg",
            content=content,
        )

        await usecase.execute()

        repository.upload.assert_awaited_once()

    async def test_upload_not_image_url(
        self: Self,
        httpx_mock: HTTPXMock,
        usecase: UploadImageURLUseCase,
    ) -> None:
        httpx_mock.add_response(
            method="HEAD",
            url="http://test.local/test.jpeg",
            headers={"Content-Type": "music/mp3", "Content-Length": "123"},
        )

        with pytest.raises(FileIsNotImageError):
            await usecase.execute()

    async def test_max_upload_size(
        self: Self,
        httpx_mock: HTTPXMock,
        usecase: UploadImageURLUseCase,
    ) -> None:
        httpx_mock.add_response(
            method="HEAD",
            url="http://test.local/test.jpeg",
            headers={
                "Content-Type": "image/jpeg",
                "Content-Length": "5000001",
            },
        )

        with pytest.raises(FileIsTooLargeError):
            await usecase.execute()
