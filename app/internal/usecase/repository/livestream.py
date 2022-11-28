from abc import ABC, abstractmethod
from datetime import date, timedelta

from sqlalchemy import between
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import livestreams
from app.internal.entity.livestreams import CreateLiveStream
from app.schemas.livestreams import BaseLiveStream, LiveStream


class AbstractLiveStreamRepository(ABC):
    @abstractmethod
    async def get_by_id(self, live_stream_id: int) -> LiveStream | None:
        pass

    @abstractmethod
    async def get_by_slug(
        self,
        slug: str,
        start: date = date.today() - timedelta(days=2),
        end: date = date.today() + timedelta(days=31),
    ) -> LiveStream | None:
        pass

    @abstractmethod
    async def get_all(
        self,
        start: date = date.today() - timedelta(days=2),
        end: date = date.today() + timedelta(days=31),
    ) -> list[LiveStream | None]:
        pass

    @abstractmethod
    async def create(self, live_stream: CreateLiveStream) -> LiveStream:
        pass

    @abstractmethod
    async def update(self, live_stream: LiveStream) -> bool:
        pass

    @abstractmethod
    async def delete(self, live_stream_id: int) -> bool:
        pass


class PostgresLiveStreamRepository(AbstractLiveStreamRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, live_stream_id: int) -> LiveStream | None:
        query = livestreams.select().where(livestreams.c.id == live_stream_id)

        result_proxy = await self.session.execute(query)
        result = result_proxy.first()
        return LiveStream(**result) if result else None

    async def get_by_slug(
        self,
        slug: str,
        start: date = date.today() - timedelta(days=2),
        end: date = date.today() + timedelta(days=31),
    ) -> LiveStream | None:
        query = livestreams.select().where(livestreams.c.slug == slug)
        query = query.where(
            between(livestreams.c.start_time, start, end),
        )

        result_proxy = await self.session.execute(query)
        result = result_proxy.first()
        return LiveStream(**result) if result else None

    async def get_all(
        self,
        start: date = date.today() - timedelta(days=2),
        end: date = date.today() + timedelta(days=31),
    ) -> list[LiveStream | None]:
        query = livestreams.select().where(
            between(livestreams.c.start_time, start, end),
        )

        result = await self.session.stream(query)
        return [LiveStream(**row) async for row in result]

    async def create(self, live_stream: BaseLiveStream) -> LiveStream:
        query = livestreams.insert().values(**live_stream.dict())
        result = await self.session.execute(query)
        return LiveStream(
            id=result.inserted_primary_key[0],
            **live_stream.dict(),
        )

    async def update(self, live_stream: LiveStream) -> bool:
        query = livestreams.update().values(**live_stream.dict())
        query = query.where(livestreams.c.id == live_stream.id)
        result = await self.session.execute(query)
        return bool(result.rowcount)

    async def delete(self, live_stream_id: int) -> bool:
        query = livestreams.delete().where(livestreams.c.id == live_stream_id)
        result = await self.session.execute(query)
        return bool(result.rowcount)
