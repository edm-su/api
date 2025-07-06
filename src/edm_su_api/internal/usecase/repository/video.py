from abc import ABC, abstractmethod
from typing import final

from sqlalchemy import (
    ColumnExpressionArgument,
    and_,
    case,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import false
from typing_extensions import Self, override

from edm_su_api.internal.entity.video import NewVideoDto, UpdateVideoDto, Video
from edm_su_api.internal.usecase.exceptions.video import VideoNotFoundError
from edm_su_api.pkg.postgres import LikedVideos
from edm_su_api.pkg.postgres import Video as PGVideo


class AbstractVideoRepository(ABC):
    @abstractmethod
    async def get_all(
        self: Self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Video]:
        pass

    @abstractmethod
    async def get_all_with_favorite_mark(
        self: Self,
        user_id: str,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Video]:
        pass

    @abstractmethod
    async def get_by_slug(
        self: Self,
        slug: str,
    ) -> Video:
        pass

    @abstractmethod
    async def get_by_id(
        self: Self,
        id_: int,
    ) -> Video:
        pass

    @abstractmethod
    async def get_by_slug_with_favorite_mark(
        self,
        slug: str,
        user_id: str,
    ) -> Video:
        pass

    @abstractmethod
    async def get_by_yt_id(
        self: Self,
        yt_id: str,
    ) -> Video:
        pass

    @abstractmethod
    async def create(
        self: Self,
        video: NewVideoDto,
    ) -> Video:
        pass

    @abstractmethod
    async def update(
        self: Self,
        video: UpdateVideoDto,
    ) -> Video:
        pass

    @abstractmethod
    async def delete(
        self: Self,
        id_: int,
    ) -> None:
        pass

    @abstractmethod
    async def count(self: Self) -> int:
        pass


@final
class PostgresVideoRepository(AbstractVideoRepository):
    def __init__(
        self: Self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    @override
    async def get_all(
        self: Self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Video]:
        query = (
            select(PGVideo)
            .where(PGVideo.deleted == false())
            .offset(offset)
            .limit(limit)
            .order_by(PGVideo.id.desc())
        )

        result = (await self._session.scalars(query)).all()
        return [Video.model_validate(video) for video in result]

    @override
    async def get_all_with_favorite_mark(
        self: Self,
        user_id: str,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Video]:
        query = (
            (
                select(
                    PGVideo,
                    case((LikedVideos.video_id.isnot(None), True), else_=False).label(
                        "is_favorite"
                    ),
                )
            )
            .outerjoin(
                LikedVideos,
                and_(
                    PGVideo.id == LikedVideos.video_id, LikedVideos.user_id == user_id
                ),
            )
            .where(PGVideo.deleted == false())
            .offset(offset)
            .limit(limit)
            .order_by(PGVideo.id.desc())
        )

        result = (await self._session.execute(query)).all()
        videos: list[Video] = []
        for row in result:
            video = Video.model_validate(row[0])
            video.is_favorite = row[1]
            videos.append(video)
        return videos

    async def _get_by(
        self: Self,
        whereclause: ColumnExpressionArgument[bool],
    ) -> Video:
        query = select(PGVideo).where(whereclause).where(PGVideo.deleted == false())

        try:
            result = (await self._session.scalars(query)).one()
            return Video.model_validate(result)
        except NoResultFound as e:
            raise VideoNotFoundError from e

    @override
    async def get_by_slug(
        self: Self,
        slug: str,
    ) -> Video:
        return await self._get_by(PGVideo.slug == slug)

    @override
    async def get_by_yt_id(
        self: Self,
        yt_id: str,
    ) -> Video:
        return await self._get_by(PGVideo.yt_id == yt_id)

    @override
    async def get_by_id(
        self: Self,
        id_: int,
    ) -> Video:
        return await self._get_by(PGVideo.id == id_)

    @override
    async def get_by_slug_with_favorite_mark(
        self,
        slug: str,
        user_id: str,
    ) -> Video:
        query = (
            select(
                PGVideo,
                case((LikedVideos.video_id.isnot(None), True), else_=False).label(
                    "is_favorite"
                ),
            )
            .outerjoin(
                LikedVideos,
                and_(
                    PGVideo.id == LikedVideos.video_id,
                    LikedVideos.user_id == user_id,
                ),
            )
            .where(and_(PGVideo.slug == slug, PGVideo.deleted == false()))
        )

        try:
            result = (await self._session.execute(query)).one()
            video = Video.model_validate(result[0])
            video.is_favorite = result[1]
        except NoResultFound as e:
            raise VideoNotFoundError from e
        else:
            return video

    @override
    async def create(
        self: Self,
        video: NewVideoDto,
    ) -> Video:
        query = (
            insert(PGVideo)
            .values(
                title=video.title,
                slug=video.slug,
                date=video.date,
                yt_id=video.yt_id,
                yt_thumbnail=video.yt_thumbnail,
                duration=video.duration,
                is_blocked_in_russia=video.is_blocked_in_russia,
            )
            .returning(PGVideo)
        )

        result = (await self._session.scalars(query)).one()
        return Video.model_validate(result)

    @override
    async def update(
        self: Self,
        video: UpdateVideoDto,
    ) -> Video:
        query = (
            update(PGVideo)
            .where(PGVideo.slug == video.slug)
            .where(PGVideo.deleted == false())
            .values(**video.model_dump(exclude_unset=True, exclude={"slug"}))
            .returning(PGVideo)
        )

        try:
            result = (await self._session.scalars(query)).one()
            return Video.model_validate(result)
        except NoResultFound as e:
            raise VideoNotFoundError from e

    @override
    async def delete(
        self: Self,
        id_: int,
    ) -> None:
        query = (
            update(PGVideo)
            .where(PGVideo.id == id_)
            .where(PGVideo.deleted == false())
            .values(deleted=True)
            .returning(PGVideo)
        )

        try:
            _ = (await self._session.scalars(query)).one()
        except NoResultFound as e:
            raise VideoNotFoundError from e

    @override
    async def count(self: Self) -> int:
        query = (
            select(func.count()).select_from(PGVideo).where(PGVideo.deleted == false())
        )

        return (await self._session.scalars(query)).one()
