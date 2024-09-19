from collections.abc import AsyncGenerator
from functools import lru_cache

import aioboto3
from types_aiobotocore_s3.client import S3Client

from edm_su_api.internal.entity.settings import settings


@lru_cache
def get_s3_session() -> aioboto3.Session:
    return aioboto3.Session(
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_access_key,
        region_name=settings.s3_region,
    )


async def get_s3_client() -> AsyncGenerator[S3Client, None]:
    session = get_s3_session()
    async with session.client(  # pyright: ignore[reportUnknownMemberType]
        service_name="s3",
        endpoint_url=settings.s3_endpoint,
    ) as client:  # pyright: ignore[reportUnknownVariableType]
        yield client
