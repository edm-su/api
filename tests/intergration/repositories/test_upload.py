from pathlib import Path

import pytest
from typing_extensions import Self

from app.internal.usecase.repository.upload import S3UploadRepository


@pytest.fixture()
def s3_upload_repository() -> S3UploadRepository:
    return S3UploadRepository()


class TestS3Upload:
    @pytest.mark.asyncio()
    async def test_upload(
        self: Self,
        s3_upload_repository: S3UploadRepository,
    ) -> None:
        path = Path("./tests/files/test.jpeg")
        with path.open("rb") as file:
            await s3_upload_repository.upload(
                file=file,
                path="test",
            )
