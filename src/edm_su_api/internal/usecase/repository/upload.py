from abc import ABC, abstractmethod
from typing import IO

from typing_extensions import Self

from edm_su_api.internal.entity.settings import settings
from edm_su_api.pkg.s3 import s3_client


class AbstractUploadRepository(ABC):
    @abstractmethod
    async def upload(
        self: Self,
        file: IO[bytes],
        path: str,
    ) -> None:
        pass


class S3UploadRepository(AbstractUploadRepository):
    async def upload(
        self: Self,
        file: IO[bytes],
        path: str,
    ) -> None:
        async with s3_client() as client:
            await client.put_object(
                Body=file,
                Bucket=settings.s3_bucket,
                Key=path,
                ACL="public-read",
            )
