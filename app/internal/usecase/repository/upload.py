from abc import ABC
from typing import IO

from app.helpers import s3_client
from app.settings import settings


class AbstractUploadRepository(ABC):
    async def upload(self, file: IO[bytes], path: str) -> None:
        raise NotImplementedError


class S3UploadRepository(AbstractUploadRepository):
    async def upload(self, file: IO[bytes], path: str) -> None:
        async with s3_client() as client:
            await client.put_object(
                Body=file,
                Bucket=settings.s3_bucket,
                Key=path,
                ACL="public-read",
            )
