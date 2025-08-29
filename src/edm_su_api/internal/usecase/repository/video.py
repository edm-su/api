from abc import ABC, abstractmethod
from typing import final

from fastapi.encoders import jsonable_encoder
from meilisearch_python_async import Client as MeilisearchClient
from meilisearch_python_async.task import wait_for_task
from pydantic_core import to_jsonable_python
from sqlalchemy import (
    ColumnExpressionArgument,
    and_,
    case,
    func,
    insert,
    or_,
    select,
    update,
)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import false, true
from typing_extensions import Self, override

from edm_su_api.internal.entity.video import (
    DeleteType,
    NewVideoDto,
    UpdateVideoDto,
    Video,
)
from edm_su_api.internal.usecase.exceptions.video import (
    VideoAlreadyDeletedError,
    VideoNotDeletedError,
    VideoNotFoundError,
    VideoRestoreError,
)
from edm_su_api.pkg.meilisearch import normalize_ms_index_name
from edm_su_api.pkg.postgres import LikedVideos
from edm_su_api.pkg.postgres import Video as PGVideo


class AbstractVideoRepository(ABC):
    @abstractmethod
    async def get_all(
        self: Self,
        offset: int = 0,
        limit: int = 20,
        *,
        include_deleted: bool = False,
    ) -> list[Video]:
        pass

    @abstractmethod
    async def get_all_with_favorite_mark(
        self: Self,
        user_id: str,
        offset: int = 0,
        limit: int = 20,
        *,
        include_deleted: bool = False,
    ) -> list[Video]:
        pass

    @abstractmethod
    async def get_by_slug(
        self: Self,
        slug: str,
        *,
        include_deleted: bool = False,
    ) -> Video:
        pass

    @abstractmethod
    async def get_by_id(
        self: Self,
        id_: int,
        *,
        include_deleted: bool = False,
    ) -> Video:
        pass

    @abstractmethod
    async def get_by_slug_with_favorite_mark(
        self,
        slug: str,
        user_id: str,
        *,
        include_deleted: bool = False,
    ) -> Video:
        pass

    @abstractmethod
    async def get_by_yt_id(
        self: Self,
        yt_id: str,
        *,
        include_deleted: bool = False,
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
        type_: DeleteType = DeleteType.PERMANENT,
    ) -> None:
        pass

    @abstractmethod
    async def count(self: Self, *, include_deleted: bool = False) -> int:
        pass

    @abstractmethod
    async def restore(
        self: Self,
        id_: int,
    ) -> Video:
        pass


class AbstractFullTextVideoRepository(ABC):
    @abstractmethod
    async def create(
        self: Self,
        video: Video,
    ) -> Video:
        pass

    @abstractmethod
    async def delete(
        self: Self,
        id_: int,
    ) -> None:
        pass

    @abstractmethod
    async def update(
        self,
        id_: int,
        updated_data: UpdateVideoDto,
    ) -> None:
        pass

    @abstractmethod
    async def restore(
        self: Self,
        video: Video,
    ) -> Video:
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
        *,
        include_deleted: bool = False,
    ) -> list[Video]:
        query = (
            select(PGVideo)
            .offset(offset)
            .limit(limit)
            .order_by(PGVideo.id.desc())
            .where(
                or_(
                    PGVideo.delete_type != DeleteType.PERMANENT,
                    PGVideo.delete_type == None,  # noqa: E711
                )
            )
        )

        if not include_deleted:
            query = query.where(PGVideo.deleted == false())

        result = (await self._session.scalars(query)).all()
        return [Video.model_validate(video) for video in result]

    @override
    async def get_all_with_favorite_mark(
        self: Self,
        user_id: str,
        offset: int = 0,
        limit: int = 20,
        *,
        include_deleted: bool = False,
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
            .offset(offset)
            .limit(limit)
            .order_by(PGVideo.id.desc())
            .where(
                or_(
                    PGVideo.delete_type != DeleteType.PERMANENT,
                    PGVideo.delete_type == None,  # noqa: E711
                )
            )
        )

        if not include_deleted:
            query = query.where(PGVideo.deleted == false())

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
        *,
        include_deleted: bool = False,
    ) -> Video:
        query = (
            select(PGVideo)
            .where(whereclause)
            .where(
                or_(
                    PGVideo.delete_type != DeleteType.PERMANENT,
                    PGVideo.delete_type == None,  # noqa: E711
                )
            )
        )

        if not include_deleted:
            query = query.where(PGVideo.deleted == false())

        try:
            result = (await self._session.scalars(query)).one()
            return Video.model_validate(result)
        except NoResultFound as e:
            raise VideoNotFoundError from e

    @override
    async def get_by_slug(
        self: Self,
        slug: str,
        *,
        include_deleted: bool = False,
    ) -> Video:
        return await self._get_by(PGVideo.slug == slug, include_deleted=include_deleted)

    @override
    async def get_by_yt_id(
        self: Self,
        yt_id: str,
        *,
        include_deleted: bool = False,
    ) -> Video:
        return await self._get_by(
            PGVideo.yt_id == yt_id, include_deleted=include_deleted
        )

    @override
    async def get_by_id(
        self: Self,
        id_: int,
        *,
        include_deleted: bool = False,
    ) -> Video:
        return await self._get_by(PGVideo.id == id_, include_deleted=include_deleted)

    @override
    async def get_by_slug_with_favorite_mark(
        self,
        slug: str,
        user_id: str,
        *,
        include_deleted: bool = False,
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
            .where(PGVideo.slug == slug)
            .where(
                or_(
                    PGVideo.delete_type != DeleteType.PERMANENT,
                    PGVideo.delete_type == None,  # noqa: E711
                )
            )
        )

        if not include_deleted:
            query = query.where(PGVideo.deleted == false())

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
        type_: DeleteType = DeleteType.PERMANENT,
    ) -> None:
        check_query = select(PGVideo).where(PGVideo.id == id_)
        try:
            video = (await self._session.scalars(check_query)).one()
        except NoResultFound as e:
            raise VideoNotFoundError from e

        # If video is already soft-deleted and we want permanent deletion, change type
        if video.deleted and type_ == DeleteType.PERMANENT:
            query = (
                update(PGVideo)
                .where(PGVideo.id == id_)
                .values(delete_type=DeleteType.PERMANENT)
                .returning(PGVideo)
            )
            try:
                _ = (await self._session.scalars(query)).one()
            except NoResultFound as e:
                raise VideoNotFoundError from e
        elif video.deleted and type_ == DeleteType.TEMPORARY:
            # Video is already soft-deleted, can't soft-delete again
            raise VideoAlreadyDeletedError
        else:
            # Soft delete the video
            query = (
                update(PGVideo)
                .where(PGVideo.id == id_)
                .where(PGVideo.deleted == false())
                .values(deleted=True, delete_type=type_)
                .returning(PGVideo)
            )

            try:
                _ = (await self._session.scalars(query)).one()
            except NoResultFound as e:
                raise VideoNotFoundError from e

    @override
    async def count(self: Self, *, include_deleted: bool = False) -> int:
        query = (
            select(func.count())
            .select_from(PGVideo)
            .where(
                or_(
                    PGVideo.delete_type != DeleteType.PERMANENT,
                    PGVideo.delete_type == None,  # noqa: E711
                )
            )
        )

        # Only filter out deleted videos if include_deleted is False
        if not include_deleted:
            query = query.where(PGVideo.deleted == false())

        return (await self._session.scalars(query)).one()

    @override
    async def restore(
        self: Self,
        id_: int,
    ) -> Video:
        check_query = select(PGVideo).where(PGVideo.id == id_)
        try:
            video = (await self._session.scalars(check_query)).one()
        except NoResultFound as e:
            raise VideoNotFoundError from e

        if not video.deleted:
            raise VideoNotDeletedError

        # Check if video is permanently deleted - cannot restore permanently deleted
        if video.delete_type == DeleteType.PERMANENT:
            raise VideoNotDeletedError

        query = (
            update(PGVideo)
            .where(PGVideo.id == id_)
            .where(PGVideo.deleted == true())
            .values(deleted=False, delete_type=None)
            .returning(PGVideo)
        )

        try:
            result = (await self._session.scalars(query)).one()
            return Video.model_validate(result)
        except NoResultFound as e:
            msg = "Failed to restore video"
            raise VideoRestoreError(msg) from e


@final
class MeilisearchVideoRepository(AbstractFullTextVideoRepository):
    def __init__(
        self: Self,
        client: MeilisearchClient,
    ) -> None:
        self.client = client
        index_name = normalize_ms_index_name("videos")
        self.index = self.client.index(index_name)

    @override
    async def create(
        self: Self,
        video: Video,
    ) -> Video:
        # Only add to search index if video is not soft-deleted
        # Soft-deleted videos should be excluded from search results by default
        if not video.deleted:
            documents = [jsonable_encoder(video, exclude={"is_blocked_in_russia"})]
            task = await self.index.add_documents(documents)
            _ = await wait_for_task(self.client.http_client, task.task_uid)
        return video

    @override
    async def delete(
        self: Self,
        id_: int,
    ) -> None:
        # Remove video from search index when soft-deleted
        # This ensures soft-deleted videos are excluded from search results
        task = await self.index.delete_documents([str(id_)])
        _ = await wait_for_task(self.client.http_client, task.task_uid)

    @override
    async def update(self, id_: int, updated_data: UpdateVideoDto) -> None:
        data = updated_data.model_dump(
            exclude={"is_blocked_in_russia", "slug"},
            exclude_unset=True,
        )
        data["id"] = id_
        documents = [to_jsonable_python(data)]
        task = await self.index.update_documents(documents)
        _ = await wait_for_task(self.client.http_client, task_id=task.task_uid)

    @override
    async def restore(
        self: Self,
        video: Video,
    ) -> Video:
        # Re-add video to search index when restored
        # This ensures restored videos are included in search results again
        documents = [jsonable_encoder(video, exclude={"is_blocked_in_russia"})]
        task = await self.index.add_documents(documents)
        _ = await wait_for_task(self.client.http_client, task.task_uid)
        return video
