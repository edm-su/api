from typing import IO

import pytest
from typing_extensions import Self

from app.internal.usecase.repository.upload import S3UploadRepository


@pytest.fixture()
def s3_upload_repository() -> S3UploadRepository:
    return S3UploadRepository()


class TestS3Upload:
    async def test_upload(
        self: Self,
        s3_upload_repository: S3UploadRepository,
        image: IO[bytes],
    ) -> None:
        await s3_upload_repository.upload(
            file=image,
            path="test",
        )
