from authzed.api.v1 import Client
from grpcutil import insecure_bearer_token_credentials

from app.internal.entity.settings import settings


async def get_spicedb_client() -> Client:
    return Client(
        settings.spicedb_url,
        insecure_bearer_token_credentials(settings.spicedb_api_key),
    )
