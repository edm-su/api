from abc import ABC

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import comments
from app.internal.entity.comment import Comment, NewCommentDto


class AbstractCommentRepository(ABC):
    async def create(
        self,
        comment: NewCommentDto,
    ) -> Comment:
        pass

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Comment]:
        pass

    async def count(self) -> int:
        pass

    async def get_video_comments(self, video_id: int) -> list[Comment]:
        pass


class PostgresCommentRepository(AbstractCommentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        comment: NewCommentDto,
    ) -> Comment:
        query = comments.insert().values(**comment.dict())
        query = query.returning(comments.c.published_at)
        result_proxy = await self.session.execute(query)
        result = await result_proxy.fetchone()
        return Comment(
            id=result_proxy.inserted_primary_key[0],
            video_id=comment.video.id,
            user_id=comment.user_id,
            text=comment.text,
            published_at=result["published_at"],
        )

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Comment]:
        query = (
            comments.select()
            .offset(offset)
            .limit(limit)
            .order_by(comments.c.id)
        )
        result = await self.session.stream(query)
        return [Comment(**row) async for row in result]

    async def count(self) -> int:
        query = select([func.count()]).select_from(comments)
        result = await self.session.execute(query)
        count = await result.scalar().first()
        return count

    async def get_video_comments(self, video_id: int) -> list[Comment]:
        query = comments.select().where(comments.c.video_id == video_id)
        query = query.order_by(comments.c.id)
        result = await self.session.stream(query)
        return [Comment(**row) async for row in result]
