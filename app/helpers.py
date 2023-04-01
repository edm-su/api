import hashlib
import secrets
import string
from uuid import uuid4

import aioboto3
from botocore.client import BaseClient
from fastapi import Query
from typing_extensions import Self

from app.settings import settings


def s3_client() -> BaseClient:
    session = aioboto3.Session()
    return session.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        region_name=settings.s3_region,
        aws_secret_access_key=settings.s3_access_key,
        aws_access_key_id=settings.s3_access_key_id,
    )


def get_password_hash(password: str) -> str:
    encoded_password = f"{password}{settings.secret_key}".encode()
    return hashlib.sha256(encoded_password).hexdigest()


def generate_secret_code(n: int = 10) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for i in range(n))


class Paginator:
    def __init__(
        self: Self,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=25, ge=1, le=50),
    ) -> None:
        self.skip = skip
        self.limit = limit


def generate_token() -> str:
    token = str(uuid4()) + settings.secret_key
    return hashlib.sha256(token.encode()).hexdigest()
