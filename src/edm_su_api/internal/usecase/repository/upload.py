from abc import ABC, abstractmethod

from types_aiobotocore_s3.client import S3Client
from typing_extensions import Self

from edm_su_api.internal.entity.settings import settings


class AbstractPreSignedUploadRepository(ABC):
    @abstractmethod
    async def generate(
        self: Self,
        key: str,
        expires_in: int,
    ) -> str:
        pass


class S3PreSignedUploadRepository(AbstractPreSignedUploadRepository):
    def __init__(self: Self, s3_client: S3Client) -> None:
        self.s3_cleint = s3_client

    async def generate(self: Self, key: str, expires_in: int) -> str:
        return await self.s3_cleint.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": settings.s3_bucket, "Key": key},
            ExpiresIn=expires_in,
            HttpMethod="PUT",
        )
