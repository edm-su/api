import aiofiles
from authzed.api.v1 import Client
from grpcutil import (
    bearer_token_credentials,
    insecure_bearer_token_credentials,
)

from edm_su_api.internal.entity.settings import settings


async def get_spicedb_client() -> Client:
    token = settings.spicedb_api_key
    url = settings.spicedb_url

    if settings.spicedb_insecure:
        credentials = insecure_bearer_token_credentials(token)
    else:
        cert = None
        if settings.spicedb_tls_cert:
            async with aiofiles.open(settings.spicedb_tls_cert, "rb") as f:
                cert = await f.read()
        credentials = bearer_token_credentials(token, cert)

    return Client(url, credentials)
