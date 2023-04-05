from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from typing_extensions import Self

from app.internal.usecase.repository.upload import AbstractUploadRepository
from app.internal.usecase.upload import UploadImageUseCase
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
            usecase: UploadImageUseCase,
        ) -> None:
        await usecase.execute()

        usecase.repository.upload.assert_awaited_once()  # type: ignore[attr-defined]  # noqa: E501
