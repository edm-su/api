import aiofiles
import grpc
from authzed.api.v1 import Client
from grpc import ChannelCredentials
from grpc.experimental import insecure_channel_credentials
from grpcutil import bearer_token_credentials

from app.internal.entity.settings import settings


def insecure_bearer_token_credentials(token: str) -> ChannelCredentials:
    return grpc.composite_channel_credentials(
        insecure_channel_credentials(),
        grpc.access_token_call_credentials(token),
    )


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
