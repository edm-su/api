import aioboto3
from botocore.client import BaseClient

from app.internal.entity.settings import settings


def s3_client() -> BaseClient:
    session = aioboto3.Session()
    return session.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        region_name=settings.s3_region,
        aws_secret_access_key=settings.s3_access_key,
        aws_access_key_id=settings.s3_access_key_id,
    )
