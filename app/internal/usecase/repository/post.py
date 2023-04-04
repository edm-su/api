from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import posts
from app.helpers import Paginator
from app.internal.entity.post import NewPostDTO, Post


class AbstractPostRepository(ABC):
    @abstractmethod
    async def create(
        self,
        post: NewPostDTO,
    ) -> Post:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> None | Post:
        pass

    @abstractmethod
    async def get_all(self, paginator: Paginator) -> list[None | Post]:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass

    @abstractmethod
    async def delete(self, post: Post) -> bool:
        pass


class PostgresPostRepository(AbstractPostRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, post: NewPostDTO) -> Post:
        post.published_at = post.published_at.replace(tzinfo=None)
        query = posts.insert().values(**post.dict())
        result = await self.session.execute(query)
        return Post(
            id=result.inserted_primary_key[0],
            title=post.title,
            text=post.text,
            slug=post.slug,
            published_at=post.published_at,
            user_id=post.user.id,
            annotation=post.annotation,
            thumbnail=post.thumbnail,
        )

    async def get_by_slug(self, slug: str) -> None | Post:
        query = posts.select().where(posts.c.slug == slug)
        query = query.where(posts.c.published_at <= datetime.now())

        result_proxy = await self.session.execute(query)
        result = result_proxy.first()

        return (
            Post(
                id=result.id,
                title=result.title,
                text=result.text,
                slug=result.slug,
                published_at=result.published_at,
                user_id=result.user_id,
                annotation=result.annotation,
                thumbnail=result.thumbnail,
            )
            if result
            else None
        )

    async def get_all(self, paginator: Paginator) -> list[None | Post]:
        query = posts.select().where(posts.c.published_at <= datetime.now())
        query = query.order_by(posts.c.published_at.desc())
        query = query.offset(paginator.skip).limit(paginator.limit)

        result = await self.session.stream(query)

        return [Post(**row) async for row in result]

    async def count(self) -> int:
        query = select([func.count()]).select_from(posts)
        result = await self.session.execute(query)
        return result.scalar()

    async def delete(self, post: Post) -> bool:
        query = posts.delete().where(posts.c.id == post.id)
        result = await self.session.execute(query)
        return bool(result.rowcount)
