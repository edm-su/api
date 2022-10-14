import pytest
from pytest_mock import MockerFixture

from app.internal.usecase.repository.upload import (
    AbstractUploadRepository,
    S3UploadRepository,
)
from app.internal.usecase.upload import UploadImageUseCase


@pytest.fixture
def repository() -> S3UploadRepository:
    return S3UploadRepository()


class TestUploadImageUseCase:
    @pytest.fixture(autouse=True)
    def mock(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "app.internal.usecase.repository.upload.S3UploadRepository.upload",
            return_value=None,
        )

    @pytest.fixture
    def usecase(
        self,
        repository: AbstractUploadRepository,
    ) -> UploadImageUseCase:
        with open("tests/files/test.jpeg", "rb") as f:
            yield UploadImageUseCase(repository, f)

    async def test_upload_image(self, usecase: UploadImageUseCase) -> None:
        await usecase.execute()

        usecase.repository.upload: AsyncMock  # type: ignore
        usecase.repository.upload.assert_awaited_once()
