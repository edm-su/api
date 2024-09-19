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
    AbstractPreSignedUploadRepository,
    AbstractUploadRepository,
)
from edm_su_api.internal.usecase.upload import (
    GeneratePreSignedUploadUseCase,
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


class TestGeneratePreSignedUploadUseCase:
    @pytest.fixture
    def repository(self: Self) -> AbstractPreSignedUploadRepository:
        return AsyncMock(spec=AbstractPreSignedUploadRepository)

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GeneratePreSignedUploadUseCase:
        return GeneratePreSignedUploadUseCase(repository)

    async def test_generate_pre_signed_url(
        self: Self,
        usecase: GeneratePreSignedUploadUseCase,
        repository: AsyncMock,
    ) -> None:
        key = "test_key"
        expires_in = 1800
        expected_url = "https://pre-signed-url.com"

        repository.generate.return_value = expected_url

        result = await usecase.execute(key, expires_in)

        assert result == expected_url
        repository.generate.assert_awaited_once_with(key, expires_in)


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
