import hashlib
import random
import string

import boto3
from algoliasearch.search_client import SearchClient
from algoliasearch.search_index import SearchIndex
from botocore.client import BaseClient
from fastapi import Query

from app.settings import settings


def algolia_client() -> SearchIndex:
    client = SearchClient.create(
        settings.algolia_app_id,
        settings.algolia_api_key,
    )
    index = client.init_index(settings.algolia_index)
    return index


def s3_client() -> BaseClient:
    s3 = boto3.client(
        's3',
        endpoint_url=settings.s3_endpoint,
        aws_secret_access_key=settings.s3_access_key,
        aws_access_key_id=settings.s3_access_key_id,
    )
    return s3


def get_password_hash(password: str) -> str:
    encoded_password = f'{password}{settings.secret_key}'.encode()
    return hashlib.sha256(encoded_password).hexdigest()


def generate_secret_code(n: int = 10) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))


class Paginator:
    def __init__(
            self,
            skip: int = Query(default=0, ge=0),
            limit: int = Query(default=25, ge=1, le=50),
    ):
        self.skip = skip
        self.limit = limit
