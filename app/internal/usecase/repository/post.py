from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from app.db import posts
from app.internal.entity.post import NewPostDTO, Post


class AbstractPostRepository(ABC):
    @abstractmethod
    async def create(
        self: Self,
        post: NewPostDTO,
    ) -> Post:
        pass

    @abstractmethod
    async def get_by_slug(
        self: Self,
        slug: str,
    ) -> None | Post:
        pass

    @abstractmethod
    async def get_all(
        self: Self,
        skip: int = 0,
        limit: int = 10,
    ) -> list[None | Post]:
        pass

    @abstractmethod
    async def count(self: Self) -> int:
        pass

    @abstractmethod
    async def delete(
        self: Self,
        post: Post,
    ) -> bool:
        pass


class PostgresPostRepository(AbstractPostRepository):
    def __init__(
        self: Self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create(
        self: Self,
        post: NewPostDTO,
    ) -> Post:
        if post.published_at:
            post.published_at = post.published_at.replace(tzinfo=None)
        values = {
            "title": post.title,
            "annotation": post.annotation,
            "text": post.text,
            "slug": post.slug,
            "published_at": post.published_at,
            "thumbnail": post.thumbnail,
            "user_id": post.user.id,
        }

        query = posts.insert().values(values)
        query = query.returning(posts.c.id)
        result = (await self.session.execute(query)).mappings().one()
        await self.session.commit()
        return Post(
            id=result["id"],
            title=post.title,
            text=post.text,
            slug=post.slug,
            published_at=post.published_at,
            user_id=post.user.id,
            annotation=post.annotation,
            thumbnail=post.thumbnail,
        )

    async def get_by_slug(
        self: Self,
        slug: str,
    ) -> None | Post:
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

    async def get_all(
        self: Self,
        skip: int = 0,
        limit: int = 10,
    ) -> list[None | Post]:
        query = posts.select().where(posts.c.published_at <= datetime.now())
        query = query.order_by(posts.c.published_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.stream(query)
        rows = await result.mappings().all()

        return [Post(**row) for row in rows]

    async def count(self: Self) -> int:
        query = select(func.count()).select_from(posts)
        query = query.where(posts.c.published_at <= datetime.now())
        result = await self.session.execute(query)
        return result.scalar_one()

    async def delete(
        self: Self,
        post: Post,
    ) -> bool:
        query = (
            posts.delete()
            .returning(posts.c.id)
            .where(
                posts.c.id == post.id,
            )
        )
        result = (await self.session.execute(query)).scalar_one_or_none()
        return bool(result)
