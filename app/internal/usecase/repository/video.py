from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from fastapi.encoders import jsonable_encoder
from meilisearch_python_async import Client as MeilisearchClient
from meilisearch_python_async.errors import MeilisearchError
from meilisearch_python_async.task import wait_for_task
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

if TYPE_CHECKING:
    from sqlalchemy.engine import Result

from app.db import videos
from app.internal.entity.video import NewVideoDto, Video
from app.internal.usecase.repository.exceptions.full_text import (
    FullTextRepositoryError,
)
from app.meilisearch import normalize_ms_index_name


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
    ) -> Video | None:
        pass

    @abstractmethod
    async def get_by_id(
        self: Self,
        id_: int,
    ) -> Video | None:
        pass

    @abstractmethod
    async def get_by_yt_id(
        self: Self,
        yt_id: str,
    ) -> Video | None:
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
        id_: int,
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
        self.session = session

    async def get_all(
        self: Self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Video]:
        query = (
            select(videos).offset(offset).limit(limit).order_by(videos.c.id)
        )
        result = await self.session.stream(query)
        return [Video(**row) for row in result]

    async def get_by_slug(
        self: Self,
        slug: str,
    ) -> Video | None:
        query = select([videos]).where(videos.c.slug == slug)
        result: Result = await self.session.execute(query)
        video = result.first()
        return Video(**video) if video else None # type: ignore[return]

    async def get_by_yt_id(
        self: Self,
        yt_id: str,
    ) -> Video | None:
        query = select([videos]).where(videos.c.yt_id == yt_id)
        result: Result = await self.session.execute(query)
        video = result.first()
        return Video(**video) if video else None

    async def get_by_id(
        self: Self,
        id_: int,
    ) -> Video | None:
        query = select([videos]).where(videos.c.id == id_)
        result: Result = await self.session.execute(query)
        video = result.first()
        return Video(**video) if video else None

    async def create(
        self: Self,
        video: NewVideoDto,
    ) -> Video:
        query = videos.insert().values(**video.dict())
        result = await self.session.execute(query)
        return Video(id=result.inserted_primary_key[0], **video.dict())

    async def update(
        self: Self,
        id_: int,
        video: Video,
    ) -> Video:
        query = videos.update()
        query = query.where(videos.c.id == id_)
        query = query.values(**video.dict())
        await self.session.execute(query)
        return video

    async def delete(
        self: Self,
        id_: int,
    ) -> None:
        query = videos.delete().where(videos.c.id == id_)
        await self.session.execute(query)

    async def count(self: Self) -> int:
        query = select([func.count(videos.c.id)])
        result = await self.session.execute(query)
        return result.scalar()


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
        try:
            task = await self.index.delete_documents([str(id_)])
            await wait_for_task(self.client.http_client, task.task_uid)
        except MeilisearchError as e:
            raise FullTextRepositoryError(e) from e
