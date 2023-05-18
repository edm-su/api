import io
from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from pytest_httpx import HTTPXMock
from typing_extensions import Self

from app.internal.entity.upload import ImageURL
from app.internal.usecase.exceptions.upload import (
    FileIsNotImageError,
    FileIsTooLargeError,
)
from app.internal.usecase.repository.upload import AbstractUploadRepository
from app.internal.usecase.upload import (
    UploadImageURLUseCase,
    UploadImageUseCase,
)
from app.settings import settings


@pytest.fixture()
def repository() -> AbstractUploadRepository:
    return AsyncMock(repr=AbstractUploadRepository)


class TestUploadImageUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        settings.static_url = "https://test.local"
        repository.upload.return_value = None

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> Generator[UploadImageUseCase, None, None]:
        path = Path("tests/files/test.jpeg")
        with path.open("rb") as f:
            yield UploadImageUseCase(repository, f)

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
    def _mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        settings.static_url = "https://test.local"
        repository.upload.return_value = None

    @pytest.fixture()
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
    ) -> None:
        httpx_mock.add_response(
            method="HEAD",
            url="http://test.local/test.jpeg",
            headers={"Content-Type": "image/jpeg", "Content-Length": "123"},
        )
        path = Path("tests/files/test.jpeg")
        with path.open("rb") as f:
            httpx_mock.add_response(
                method="GET",
                url="http://test.local/test.jpeg",
                content=f.read(),
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
