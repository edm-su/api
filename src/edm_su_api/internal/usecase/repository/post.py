from abc import ABC, abstractmethod
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from edm_su_api.internal.entity.post import (
    NewPostDTO,
    Post,
    PostEditHistory,
    UpdatePostDTO,
)
from edm_su_api.internal.usecase.exceptions.post import PostNotFoundError
from edm_su_api.pkg.postgres import Post as PGPost
from edm_su_api.pkg.postgres import PostEditHistory as PGPostEditHistory


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

    @abstractmethod
    async def update(
        self: Self,
        post_id: int,
        update_data: UpdatePostDTO,
    ) -> Post:
        pass


class AbstractPostHistoryRepository(ABC):
    @abstractmethod
    async def create(
        self: Self,
        post_id: int,
        description: str,
        edited_by: UUID,
    ) -> PostEditHistory:
        pass

    @abstractmethod
    async def get_by_post_id(
        self: Self,
        post_id: int,
    ) -> list[PostEditHistory]:
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

    async def update(
        self: Self,
        post_id: int,
        update_data: UpdatePostDTO,
    ) -> Post:
        update_values: dict[str, str | datetime | UUID | dict] = {}

        if update_data.title is not None:
            update_values["title"] = update_data.title
        if update_data.annotation is not None:
            update_values["annotation"] = update_data.annotation
        if update_data.text is not None:
            update_values["text"] = update_data.text
        if update_data.thumbnail is not None:
            update_values["thumbnail"] = update_data.thumbnail
        if update_data.published_at is not None:
            update_values["published_at"] = update_data.published_at

        update_values["updated_at"] = datetime.now(tz=timezone.utc)
        update_values["updated_by"] = UUID(update_data.user.id)

        query = (
            update(PGPost)
            .where(PGPost.id == post_id)
            .values(**update_values)
            .returning(PGPost)
        )

        try:
            result = (await self._session.scalars(query)).one()
            return Post.model_validate(result)
        except NoResultFound as e:
            raise PostNotFoundError from e


class PostgresPostHistoryRepository(AbstractPostHistoryRepository):
    def __init__(
        self: Self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self: Self,
        post_id: int,
        description: str,
        edited_by: UUID,
    ) -> PostEditHistory:
        query = (
            insert(PGPostEditHistory)
            .values(
                post_id=post_id,
                description=description,
                edited_by=edited_by,
            )
            .returning(PGPostEditHistory)
        )

        result = (await self._session.scalars(query)).one()
        return PostEditHistory.model_validate(result, from_attributes=True)

    async def get_by_post_id(
        self: Self,
        post_id: int,
    ) -> list[PostEditHistory]:
        query = (
            select(PGPostEditHistory)
            .where(PGPostEditHistory.post_id == post_id)
            .order_by(PGPostEditHistory.edited_at.desc())
        )

        results = (await self._session.scalars(query)).all()
        return [
            PostEditHistory.model_validate(h, from_attributes=True) for h in results
        ]
