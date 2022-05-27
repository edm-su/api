from abc import ABC
from typing import Any

from asyncpg import UniqueViolationError
from databases import Database
from sqlalchemy import and_, false, select

from app.db import liked_videos, videos
from app.schemas.user import User
from app.schemas.video import DbVideo, PgVideo


class UserVideoRepository(ABC):
    async def like_video(self, user: User, video: DbVideo) -> bool:
        pass

    async def unlike_video(self, user: User, video: DbVideo) -> bool:
        pass

    async def get_liked_videos(
        self,
        user: User,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[DbVideo | None]:
        pass

    async def is_liked(self, user: User, video: DbVideo) -> bool:
        pass


class PostgresUserVideoRepository(UserVideoRepository):
    def __init__(self, session: Database):
        self.__session = session

    async def like_video(self, user: User, video: DbVideo) -> bool:
        query = liked_videos.insert().values(
            user_id=user.id,
            video_id=video.id,
        )
        return await self.__execute(query)

    async def unlike_video(self, user: User, video: DbVideo) -> bool:
        query = liked_videos.delete().where(
            (liked_videos.c.user_id == user.id)
            & (liked_videos.c.video_id == video.id)
        )
        return await self.__execute(query)

    async def __execute(
        self,
        query: Any,
    ) -> bool:
        try:
            query = query.returning(liked_videos)
            return bool(await self.__session.fetch_one(query))
        except UniqueViolationError:
            return False

    async def get_liked_videos(
        self,
        user: User,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[DbVideo | None]:
        query = (
            select([videos])
            .select_from(
                liked_videos.join(
                    videos,
                    and_(
                        videos.c.id == liked_videos.c.video_id,
                        videos.c.deleted == false(),
                    ),
                )
            )
            .where(liked_videos.c.user_id == user.id)
            .limit(limit)
            .offset(offset)
            .order_by(liked_videos.c.created_at.desc())
        )
        db_videos = await self.__session.fetch_all(query)
        return [PgVideo(**video) for video in db_videos]

    async def is_liked(self, user: User, video: DbVideo) -> bool:
        query = liked_videos.select().where(
            (liked_videos.c.user_id == user.id)
            & (liked_videos.c.video_id == video.id)
        )
        return await self.__session.fetch_val(query) is not None
