import nats
from nats.aio.client import Client
from nats.js.client import JetStreamContext
from typing_extensions import Self


class NatsClient:
    _connection: Client
    jetstream: JetStreamContext

    async def connect(
        self: Self,
        servers: list[str],
    ) -> None:
        self._connection = await nats.connect(servers)
        self.jetstream = self._connection.jetstream()

    async def publish(
        self: Self,
        subject: str,
        payload: bytes,
    ) -> None:
        await self.jetstream.publish(subject, payload)

    async def close(self: Self) -> None:
        await self._connection.close()


nats_client = NatsClient()
