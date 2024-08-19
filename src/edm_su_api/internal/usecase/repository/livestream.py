from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import between, delete, insert, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from edm_su_api.internal.entity.livestreams import (
    CreateLiveStreamDTO,
    LiveStream,
)
from edm_su_api.internal.usecase.exceptions.livestream import (
    LiveStreamNotFoundError,
)
from edm_su_api.pkg.postgres import LiveStream as PGLiveStream


class AbstractLiveStreamRepository(ABC):
    @abstractmethod
    async def get_by_id(
        self: Self,
        live_stream_id: int,
    ) -> LiveStream:
        pass

    @abstractmethod
    async def get_by_slug(
        self: Self,
        slug: str,
        start: date | None = None,
        end: date | None = None,
    ) -> LiveStream:
        pass

    @abstractmethod
    async def get_all(
        self: Self,
        start: date | None = None,
        end: date | None = None,
    ) -> list[LiveStream]:
        pass

    @abstractmethod
    async def create(
        self: Self,
        live_stream: CreateLiveStreamDTO,
    ) -> LiveStream:
        pass

    @abstractmethod
    async def update(
        self: Self,
        live_stream: LiveStream,
    ) -> None:
        pass

    @abstractmethod
    async def delete(
        self: Self,
        live_stream_id: int,
    ) -> None:
        pass


class PostgresLiveStreamRepository(AbstractLiveStreamRepository):
    def __init__(
        self: Self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def get_by_id(
        self: Self,
        live_stream_id: int,
    ) -> LiveStream:
        query = select(PGLiveStream).where(PGLiveStream.id == live_stream_id)

        try:
            result = (await self._session.scalars(query)).one()
            return LiveStream.model_validate(result)
        except NoResultFound as e:
            raise LiveStreamNotFoundError from e

    async def get_by_slug(
        self: Self,
        slug: str,
        start: date | None = None,
        end: date | None = None,
    ) -> LiveStream:
        if start is None:
            start = datetime.now(tz=timezone.utc).date() - timedelta(days=2)

        if end is None:
            end = datetime.now(tz=timezone.utc).date() + timedelta(days=31)

        query = (
            select(PGLiveStream)
            .where(PGLiveStream.slug == slug)
            .where(
                between(PGLiveStream.start_time, start, end),
            )
        )

        try:
            result = (await self._session.scalars(query)).one()
            return LiveStream.model_validate(result)
        except NoResultFound as e:
            raise LiveStreamNotFoundError from e

    async def get_all(
        self: Self,
        start: date | None = None,
        end: date | None = None,
    ) -> list[LiveStream]:
        if start is None:
            start = datetime.now(tz=timezone.utc).date() - timedelta(days=2)

        if end is None:
            end = datetime.now(tz=timezone.utc).date() + timedelta(days=31)

        query = select(PGLiveStream).where(
            between(PGLiveStream.start_time, start, end),
        )

        result = (await self._session.scalars(query)).all()
        return [LiveStream.model_validate(livestream) for livestream in result]

    async def create(
        self: Self,
        live_stream: CreateLiveStreamDTO,
    ) -> LiveStream:
        query = (
            insert(PGLiveStream)
            .values(
                title=live_stream.title,
                slug=live_stream.slug,
                start_time=live_stream.start_time,
                end_time=live_stream.end_time,
                image=live_stream.image,
                genres=live_stream.genres,
                url=str(live_stream.url),
            )
            .returning(PGLiveStream)
        )
        result = (await self._session.scalars(query)).one()

        return LiveStream.model_validate(result)

    async def update(
        self: Self,
        live_stream: LiveStream,
    ) -> None:
        values = live_stream.model_dump(exclude_unset=True)
        if "url" in values:
            values["url"] = str(live_stream.url)

        query = (
            update(PGLiveStream)
            .where(PGLiveStream.id == live_stream.id)
            .values(values)
            .returning(PGLiveStream)
        )

        try:
            (await self._session.scalars(query)).one()
        except NoResultFound as e:
            raise LiveStreamNotFoundError from e

    async def delete(
        self: Self,
        live_stream_id: int,
    ) -> None:
        query = (
            delete(PGLiveStream)
            .where(PGLiveStream.id == live_stream_id)
            .returning(PGLiveStream)
        )

        try:
            (await self._session.scalars(query)).one()
        except NoResultFound as e:
            raise LiveStreamNotFoundError from e
