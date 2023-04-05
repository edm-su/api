from abc import ABC, abstractmethod
from typing import IO

from typing_extensions import Self

from app.helpers import s3_client
from app.settings import settings


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
