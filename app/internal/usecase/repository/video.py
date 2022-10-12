from abc import ABC

from fastapi.encoders import jsonable_encoder
from meilisearch_python_async import Client as MeilisearchClient
from meilisearch_python_async.task import wait_for_task
from sqlalchemy import func, select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import videos
from app.internal.entity.video import NewVideoDto, Video
from app.meilisearch import normalize_ms_index_name


class AbstractVideoRepository(ABC):
    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Video]:
        pass

    async def get_by_slug(
        self,
        slug: str,
    ) -> Video | None:
        pass

    async def get_by_id(
        self,
        id_: int,
    ) -> Video | None:
        pass

    async def get_by_yt_id(
        self,
        yt_id: str,
    ) -> Video | None:
        pass

    async def create(
        self,
        video: NewVideoDto,
    ) -> Video:
        pass

    async def update(
        self,
        id_: int,
        video: Video,
    ) -> Video:
        pass

    async def delete(
        self,
        id_: int,
    ) -> None:
        pass

    async def count(self) -> int:
        pass


class AbstractFullTextVideoRepository(ABC):
    async def create(self, video: Video) -> Video:
        pass

    async def delete(self, id_: int) -> None:
        pass


class PostgresVideoRepository(AbstractVideoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Video]:
        query = (
            select(videos).offset(offset).limit(limit).order_by(videos.c.id)
        )
        result = await self.session.stream(query)
        return [Video(**row) async for row in result]

    async def get_by_slug(
        self,
        slug: str,
    ) -> Video | None:
        query = select([videos]).where(videos.c.slug == slug)
        result: Result = await self.session.execute(query)
        video = result.first()
        return Video(**video) if video else None

    async def get_by_yt_id(
        self,
        yt_id: str,
    ) -> Video | None:
        query = select([videos]).where(videos.c.yt_id == yt_id)
        result: Result = await self.session.execute(query)
        video = result.first()
        return Video(**video) if video else None

    async def get_by_id(
        self,
        id_: int,
    ) -> Video | None:
        query = select([videos]).where(videos.c.id == id_)
        result: Result = await self.session.execute(query)
        video = result.first()
        return Video(**video) if video else None

    async def create(
        self,
        video: NewVideoDto,
    ) -> Video:
        query = videos.insert().values(**video.dict())
        result = await self.session.execute(query)
        return Video(id=result.inserted_primary_key[0], **video.dict())

    async def update(
        self,
        id_: int,
        video: Video,
    ) -> Video:
        pass

    async def delete(
        self,
        id_: int,
    ) -> None:
        query = videos.delete().where(videos.c.id == id_)
        await self.session.execute(query)

    async def count(self) -> int:
        query = select([func.count(videos.c.id)])
        result = await self.session.execute(query)
        return result.scalar()


class MeilisearchVideoRepository(AbstractFullTextVideoRepository):
    def __init__(self, client: MeilisearchClient) -> None:
        self.client = client
        index_name = normalize_ms_index_name("videos")
        self.index = self.client.index(index_name)

    async def create(
        self,
        video: Video,
    ) -> Video:
        documents = [jsonable_encoder(video)]
        task = await self.index.add_documents(documents)
        await wait_for_task(self.client.http_client, task.uid)
        return video

    async def delete(
        self,
        id_: int,
    ) -> None:
        task = await self.index.delete_documents([str(id_)])
        await wait_for_task(self.client.http_client, task.uid)
