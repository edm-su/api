from abc import ABC, abstractmethod

from sqlalchemy import delete, insert, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from app.internal.entity.user import User
from app.internal.entity.video import Video
from app.internal.usecase.exceptions.user_videos import UserVideoNotLikedError
from app.pkg.postgres import LikedVideos as PGLikedVideo
from app.pkg.postgres import User as PGUser
from app.pkg.postgres import Video as PGVideo


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
        query = insert(PGLikedVideo).values(
            user_id=user.id,
            video_id=video.id,
        )

        await self._session.execute(query)

    async def unlike_video(
        self: Self,
        user: User,
        video: Video,
    ) -> None:
        query = (
            delete(PGLikedVideo)
            .where(
                (PGLikedVideo.c.user_id == user.id)
                & (PGLikedVideo.c.video_id == video.id),
            )
            .returning(PGLikedVideo)
        )

        try:
            (await self._session.scalars(query)).one()
        except NoResultFound as e:
            raise UserVideoNotLikedError from e

    async def get_user_videos(
        self: Self,
        user: User,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Video]:
        query = (
            select(PGUser, PGVideo)
            .join(PGUser.liked_videos)
            .where(PGUser.id == user.id)
            .limit(limit)
            .offset(offset)
            .order_by(PGVideo.date.desc())
        )

        result = (await self._session.execute(query)).all()
        return [Video.model_validate(video[1]) for video in result]

    async def is_liked(
        self: Self,
        user: User,
        video: Video,
    ) -> bool:
        query = select(PGLikedVideo).where(
            (PGLikedVideo.c.user_id == user.id)
            & (PGLikedVideo.c.video_id == video.id),
        )

        return bool(await self._session.scalar(query))
