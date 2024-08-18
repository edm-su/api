from abc import ABC, abstractmethod

from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from edm_su_api.internal.entity.comment import Comment, NewCommentDto
from edm_su_api.pkg.postgres import Comment as PGComment


class AbstractCommentRepository(ABC):
    @abstractmethod
    async def create(
        self: Self,
        comment: NewCommentDto,
    ) -> Comment:
        pass

    @abstractmethod
    async def get_all(
        self: Self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Comment]:
        pass

    @abstractmethod
    async def count(self: Self) -> int:
        pass

    @abstractmethod
    async def get_video_comments(
        self: Self,
        video_id: int,
    ) -> list[Comment]:
        pass


class PostgresCommentRepository(AbstractCommentRepository):
    def __init__(
        self: Self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self: Self,
        comment: NewCommentDto,
    ) -> Comment:
        query = (
            insert(PGComment)
            .values(
                text=comment.text,
                user_id=comment.user.id,
                video_id=comment.video.id,
            )
            .returning(PGComment)
        )

        result = (await self._session.scalars(query)).one()
        return Comment.model_validate(result)

    async def get_all(
        self: Self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Comment]:
        query = (
            select(PGComment)
            .offset(offset)
            .limit(limit)
            .order_by(PGComment.id)
        )

        result = (await self._session.scalars(query)).all()
        return [Comment.model_validate(comment) for comment in result]

    async def count(self: Self) -> int:
        query = select(func.count()).select_from(PGComment)

        return (await self._session.scalars(query)).one()

    async def get_video_comments(
        self: Self,
        video_id: int,
    ) -> list[Comment]:
        query = (
            select(PGComment)
            .where(PGComment.video_id == video_id)
            .order_by(PGComment.id)
        )

        result = (await self._session.scalars(query)).all()
        return [Comment.model_validate(comment) for comment in result]
