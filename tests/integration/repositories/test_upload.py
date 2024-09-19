from collections.abc import AsyncGenerator
from typing import IO

import pytest
from types_aiobotocore_s3.client import S3Client
from typing_extensions import Self

from edm_su_api.internal.usecase.repository.upload import (
    S3PreSignedUploadRepository,
    S3UploadRepository,
)
from edm_su_api.pkg.s3 import get_s3_client


@pytest.fixture
async def s3_client() -> AsyncGenerator[S3Client, None]:
    async for client in get_s3_client():
        yield client


@pytest.fixture
async def s3_upload_repository(s3_client: S3Client) -> S3UploadRepository:
    return S3UploadRepository(s3_client)


@pytest.fixture
async def s3_pre_signed_upload_repository(
    s3_client: S3Client,
) -> S3PreSignedUploadRepository:
    return S3PreSignedUploadRepository(s3_client)


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
        url = await s3_pre_signed_upload_repository.generate(
            key=key, expires_in=expires_in
        )
        assert isinstance(url, str)
        assert url.startswith("http")
