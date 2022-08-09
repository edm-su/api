from abc import ABC

from sqlalchemy import (
    select,
    func,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.db import videos
from app.internal.entity.video import (
    Video,
    NewVideoDto,
)


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
        pass

    async def get_by_id(
        self,
        id_: int,
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
        query = select([func.count(videos.c.id)])
        result = await self.session.execute(query)
        return result.scalar()
