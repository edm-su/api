from abc import ABC, abstractmethod

from fastapi.encoders import jsonable_encoder
from meilisearch_python_async import Client as MeilisearchClient
from meilisearch_python_async.task import wait_for_task
from sqlalchemy import ColumnExpressionArgument, func, insert, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import false
from typing_extensions import Self

from app.internal.entity.video import NewVideoDto, Video
from app.internal.usecase.exceptions.video import VideoNotFoundError
from app.pkg.meilisearch import normalize_ms_index_name
from app.pkg.postgres import Video as PGVideo


class AbstractVideoRepository(ABC):
    @abstractmethod
    async def get_all(
        self: Self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Video]:
        pass

    @abstractmethod
    async def get_by_slug(
        self: Self,
        slug: str,
    ) -> Video:
        pass

    @abstractmethod
    async def get_by_id(
        self: Self,
        id_: int,
    ) -> Video:
        pass

    @abstractmethod
    async def get_by_yt_id(
        self: Self,
        yt_id: str,
    ) -> Video:
        pass

    @abstractmethod
    async def create(
        self: Self,
        video: NewVideoDto,
    ) -> Video:
        pass

    @abstractmethod
    async def update(
        self: Self,
        video: Video,
    ) -> Video:
        pass

    @abstractmethod
    async def delete(
        self: Self,
        id_: int,
    ) -> None:
        pass

    @abstractmethod
    async def count(self: Self) -> int:
        pass


class AbstractFullTextVideoRepository(ABC):
    @abstractmethod
    async def create(
        self: Self,
        video: Video,
    ) -> Video:
        pass

    @abstractmethod
    async def delete(
        self: Self,
        id_: int,
    ) -> None:
        pass


class PostgresVideoRepository(AbstractVideoRepository):
    def __init__(
        self: Self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def get_all(
        self: Self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Video]:
        query = (
            select(PGVideo)
            .where(PGVideo.deleted == false())
            .offset(offset)
            .limit(limit)
            .order_by(PGVideo.id)
        )

        result = (await self._session.scalars(query)).all()
        return [Video.from_orm(video) for video in result]

    async def _get_by(
        self: Self,
        whereclause: ColumnExpressionArgument[bool],
    ) -> Video:
        query = (
            select(PGVideo)
            .where(whereclause)
            .where(PGVideo.deleted == false())
        )

        try:
            result = (await self._session.scalars(query)).one()
            return Video.from_orm(result)
        except NoResultFound as e:
            raise VideoNotFoundError from e

    async def get_by_slug(
        self: Self,
        slug: str,
    ) -> Video:
        return await self._get_by(PGVideo.slug == slug)

    async def get_by_yt_id(
        self: Self,
        yt_id: str,
    ) -> Video:
        return await self._get_by(PGVideo.yt_id == yt_id)

    async def get_by_id(
        self: Self,
        id_: int,
    ) -> Video:
        return await self._get_by(PGVideo.id == id_)

    async def create(
        self: Self,
        video: NewVideoDto,
    ) -> Video:
        query = (
            insert(PGVideo)
            .values(
                title=video.title,
                slug=video.slug,
                date=video.date,
                yt_id=video.yt_id,
                yt_thumbnail=video.yt_thumbnail,
                duration=video.duration,
            )
            .returning(PGVideo)
        )

        result = (await self._session.scalars(query)).one()
        return Video.from_orm(result)

    async def update(
        self: Self,
        video: Video,
    ) -> Video:
        query = (
            update(PGVideo)
            .where(PGVideo.id == video.id)
            .where(PGVideo.deleted == false())
            .values(**video.dict(exclude_unset=True))
            .returning(PGVideo)
        )

        try:
            result = (await self._session.scalars(query)).one()
            return Video.from_orm(result)
        except NoResultFound as e:
            raise VideoNotFoundError from e

    async def delete(
        self: Self,
        id_: int,
    ) -> None:
        query = (
            update(PGVideo)
            .where(PGVideo.id == id_)
            .where(PGVideo.deleted == false())
            .values(deleted=True)
            .returning(PGVideo)
        )

        try:
            (await self._session.scalars(query)).one()
        except NoResultFound as e:
            raise VideoNotFoundError from e

    async def count(self: Self) -> int:
        query = (
            select(func.count())
            .select_from(PGVideo)
            .where(PGVideo.deleted == false())
        )

        return (await self._session.scalars(query)).one()


class MeilisearchVideoRepository(AbstractFullTextVideoRepository):
    def __init__(
        self: Self,
        client: MeilisearchClient,
    ) -> None:
        self.client = client
        index_name = normalize_ms_index_name("videos")
        self.index = self.client.index(index_name)

    async def create(
        self: Self,
        video: Video,
    ) -> Video:
        documents = [jsonable_encoder(video)]
        task = await self.index.add_documents(documents)
        await wait_for_task(self.client.http_client, task.task_uid)
        return video

    async def delete(
        self: Self,
        id_: int,
    ) -> None:
        task = await self.index.delete_documents([str(id_)])
        await wait_for_task(self.client.http_client, task.task_uid)
