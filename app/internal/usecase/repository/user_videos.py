from abc import ABC, abstractmethod

from sqlalchemy import and_, exists, false, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from app.db import liked_videos, videos
from app.internal.entity.user import User
from app.internal.entity.video import Video


class AbstractUserVideosRepository(ABC):
    @abstractmethod
    async def like_video(
        self: Self,
        user: User,
        video: Video,
    ) -> None:
        pass

    @abstractmethod
    async def unlike_video(
        self: Self,
        user: User,
        video: Video,
    ) -> None:
        pass

    @abstractmethod
    async def get_user_videos(
        self: Self,
        user: User,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Video]:
        pass

    @abstractmethod
    async def is_liked(
        self: Self,
        user: User,
        video: Video,
    ) -> bool:
        pass


class PostgresUserVideosRepository(AbstractUserVideosRepository):
    def __init__(
        self: Self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def like_video(
        self: Self,
        user: User,
        video: Video,
    ) -> None:
        query = liked_videos.insert().values(
            user_id=user.id,
            video_id=video.id,
        )
        await self._session.execute(query)

    async def unlike_video(
        self: Self,
        user: User,
        video: Video,
    ) -> None:
        query = liked_videos.delete().where(
            (liked_videos.c.user_id == user.id)
            & (liked_videos.c.video_id == video.id),
        )
        await self._session.execute(query)

    async def get_user_videos(
        self: Self,
        user: User,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Video]:
        query = (
            select(videos)
            .select_from(
                liked_videos.join(
                    videos,
                    and_(
                        videos.c.id == liked_videos.c.video_id,
                        videos.c.deleted == false(),
                    ),
                ),
            )
            .where(liked_videos.c.user_id == user.id)
            .limit(limit)
            .offset(offset)
            .order_by(liked_videos.c.created_at.desc())
        )
        result = (await self._session.execute(query)).mappings().all()
        return [Video(**video) for video in result]

    async def is_liked(
        self: Self,
        user: User,
        video: Video,
    ) -> bool:
        query = select(
            exists().where(
                and_(
                    liked_videos.c.user_id == user.id,
                    liked_videos.c.video_id == video.id,
                    videos.c.deleted == false(),
                ),
            ),
        ).select_from(liked_videos.join(videos))
        return bool(await self._session.scalar(query))
