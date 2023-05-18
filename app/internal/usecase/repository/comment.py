from abc import ABC, abstractmethod

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from app.internal.entity.comment import Comment, NewCommentDto
from app.pkg.postgres import comments


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
    ) -> list[Comment | None]:
        pass


class PostgresCommentRepository(AbstractCommentRepository):
    def __init__(
        self: Self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create(
        self: Self,
        comment: NewCommentDto,
    ) -> Comment:
        query = (
            comments.insert()
            .values(
                **comment.dict(exclude={"user", "video"}),
                user_id=comment.user.id,
                video_id=comment.video.id,
            )
            .returning(comments.c.id, comments.c.published_at)
        )

        result = (await self.session.execute(query)).mappings().one()
        await self.session.commit()
        return Comment(
            id=result["id"],
            video_id=comment.video.id,
            user_id=comment.user.id,
            text=comment.text,
            published_at=result["published_at"],
        )

    async def get_all(
        self: Self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Comment]:
        query = (
            comments.select()
            .offset(offset)
            .limit(limit)
            .order_by(comments.c.id)
        )

        result = (await self.session.execute(query)).mappings().all()
        return [Comment(**row) for row in result]

    async def count(self: Self) -> int:
        query = select(func.count()).select_from(comments)

        return (await self.session.execute(query)).scalar_one()

    async def get_video_comments(
        self: Self,
        video_id: int,
    ) -> list[Comment | None]:
        query = (
            comments.select()
            .where(comments.c.video_id == video_id)
            .order_by(comments.c.id)
        )

        result = (await self.session.execute(query)).mappings().all()
        return [Comment(**row) for row in result]
