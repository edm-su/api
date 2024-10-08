from abc import ABC, abstractmethod
from datetime import datetime, timezone

from sqlalchemy import delete, func, insert, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from edm_su_api.internal.entity.post import NewPostDTO, Post
from edm_su_api.internal.usecase.exceptions.post import PostNotFoundError
from edm_su_api.pkg.postgres import Post as PGPost


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
    ) -> Post:
        pass

    @abstractmethod
    async def get_all(
        self: Self,
        skip: int = 0,
        limit: int = 10,
    ) -> list[Post]:
        pass

    @abstractmethod
    async def count(self: Self) -> int:
        pass

    @abstractmethod
    async def delete(
        self: Self,
        post: Post,
    ) -> None:
        pass


class PostgresPostRepository(AbstractPostRepository):
    def __init__(
        self: Self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self: Self,
        post: NewPostDTO,
    ) -> Post:
        query = (
            insert(PGPost)
            .values(
                title=post.title,
                annotation=post.annotation,
                text=post.text,
                slug=post.slug,
                published_at=post.published_at,
                thumbnail=post.thumbnail,
                user_id=post.user.id,
            )
            .returning(PGPost)
        )

        result = (await self._session.scalars(query)).one()
        return Post.model_validate(result)

    async def get_by_slug(
        self: Self,
        slug: str,
    ) -> Post:
        query = (
            select(PGPost)
            .where(PGPost.slug == slug)
            .where(PGPost.published_at <= datetime.now(tz=timezone.utc))
        )

        try:
            result = (await self._session.scalars(query)).one()
            return Post.model_validate(result)
        except NoResultFound as e:
            raise PostNotFoundError from e

    async def get_all(
        self: Self,
        skip: int = 0,
        limit: int = 10,
    ) -> list[Post]:
        query = (
            select(PGPost)
            .where(PGPost.published_at <= datetime.now(tz=timezone.utc))
            .order_by(PGPost.published_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = (await self._session.scalars(query)).all()
        return [Post.model_validate(post) for post in result]

    async def count(self: Self) -> int:
        query = (
            select(func.count())
            .select_from(PGPost)
            .where(PGPost.published_at <= datetime.now(tz=timezone.utc))
        )

        return (await self._session.scalars(query)).one()

    async def delete(
        self: Self,
        post: Post,
    ) -> None:
        query = delete(PGPost).where(PGPost.id == post.id).returning(PGPost)

        try:
            (await self._session.scalars(query)).one()
        except NoResultFound as e:
            raise PostNotFoundError from e
