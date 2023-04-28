from abc import ABC, abstractmethod
from datetime import date, timedelta

from sqlalchemy import between
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from app.db import livestreams
from app.internal.entity.livestreams import CreateLiveStream, LiveStream


class AbstractLiveStreamRepository(ABC):
    @abstractmethod
    async def get_by_id(
        self: Self,
        live_stream_id: int,
    ) -> LiveStream | None:
        pass

    @abstractmethod
    async def get_by_slug(
        self: Self,
        slug: str,
        start: date = date.today() - timedelta(days=2),
        end: date = date.today() + timedelta(days=31),
    ) -> LiveStream | None:
        pass

    @abstractmethod
    async def get_all(
        self: Self,
        start: date = date.today() - timedelta(days=2),
        end: date = date.today() + timedelta(days=31),
    ) -> list[LiveStream | None]:
        pass

    @abstractmethod
    async def create(
        self: Self,
        live_stream: CreateLiveStream,
    ) -> LiveStream:
        pass

    @abstractmethod
    async def update(
        self: Self,
        live_stream: LiveStream,
    ) -> bool:
        pass

    @abstractmethod
    async def delete(
        self: Self,
        live_stream_id: int,
    ) -> bool:
        pass


class PostgresLiveStreamRepository(AbstractLiveStreamRepository):
    def __init__(
        self: Self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get_by_id(
        self: Self,
        live_stream_id: int,
    ) -> LiveStream | None:
        query = livestreams.select().where(livestreams.c.id == live_stream_id)

        result = (await self.session.execute(query)).mappings().first()
        return LiveStream(**result) if result else None

    async def get_by_slug(
        self: Self,
        slug: str,
        start: date = date.today() - timedelta(days=2),
        end: date = date.today() + timedelta(days=31),
    ) -> LiveStream | None:
        query = (
            livestreams.select()
            .where(livestreams.c.slug == slug)
            .where(
                between(livestreams.c.start_time, start, end),
            )
        )

        result = (await self.session.execute(query)).mappings().first()
        return LiveStream(**result) if result else None

    async def get_all(
        self: Self,
        start: date = date.today() - timedelta(days=2),
        end: date = date.today() + timedelta(days=31),
    ) -> list[LiveStream | None]:
        query = livestreams.select().where(
            between(livestreams.c.start_time, start, end),
        )

        result = (await self.session.execute(query)).mappings().all()
        return [LiveStream(**row) for row in result]

    async def create(
        self: Self,
        live_stream: CreateLiveStream,
    ) -> LiveStream:
        query = (
            livestreams.insert()
            .values(**live_stream.dict())
            .returning(livestreams.c.id)
        )

        result = (await self.session.execute(query)).scalar_one()
        return LiveStream(
            id=result,
            **live_stream.dict(),
        )

    async def update(
        self: Self,
        live_stream: LiveStream,
    ) -> bool:
        query = (
            livestreams.update()
            .values(**live_stream.dict())
            .where(livestreams.c.id == live_stream.id)
            .returning(livestreams.c.id)
        )

        result = (await self.session.execute(query)).scalar_one_or_none()
        return bool(result)

    async def delete(
        self: Self,
        live_stream_id: int,
    ) -> bool:
        query = (
            livestreams.delete()
            .where(livestreams.c.id == live_stream_id)
            .returning(livestreams.c.id)
        )

        result = (await self.session.execute(query)).scalar_one_or_none()
        return bool(result)
