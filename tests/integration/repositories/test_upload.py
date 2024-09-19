from typing import IO

import pytest
from typing_extensions import Self

from edm_su_api.internal.usecase.repository.upload import S3UploadRepository, S3PreSignedUploadRepository


@pytest.fixture
def s3_upload_repository() -> S3UploadRepository:
    return S3UploadRepository()


@pytest.fixture
def s3_pre_signed_upload_repository() -> S3PreSignedUploadRepository:
    return S3PreSignedUploadRepository()


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


class TestS3PreSignedUpload:
    async def test_generate(
        self: Self,
        s3_pre_signed_upload_repository: S3PreSignedUploadRepository,
    ) -> None:
        key = "test_key"
        expires_in = 3600
        url = await s3_pre_signed_upload_repository.generate(key=key, expires_in=expires_in)
        assert isinstance(url, str)
        assert url.startswith("https://")
