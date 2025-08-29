from typing_extensions import Self

from edm_su_api.internal.entity.video import (
    DeleteType,
    NewVideoDto,
    UpdateVideoDto,
    Video,
)
from edm_su_api.internal.usecase.exceptions.video import (
    VideoAlreadyDeletedError,
    VideoNotFoundError,
    VideoYtIdNotUniqueError,
)
from edm_su_api.internal.usecase.repository.permission import (
    AbstractPermissionRepository,
    Object,
)
from edm_su_api.internal.usecase.repository.video import (
    AbstractFullTextVideoRepository,
    AbstractVideoRepository,
)


class BaseVideoUseCase:
    def __init__(
        self: Self,
        repository: AbstractVideoRepository,
        permissions_repo: AbstractPermissionRepository | None = None,
    ) -> None:
        self.repository = repository
        self.permissions_repo = permissions_repo


class AbstractFullTextVideoUseCase(BaseVideoUseCase):
    def __init__(
        self: Self,
        repository: AbstractVideoRepository,
        full_text_repo: AbstractFullTextVideoRepository,
        permissions_repo: AbstractPermissionRepository | None = None,
    ) -> None:
        self.full_text_repo = full_text_repo
        super().__init__(repository, permissions_repo)


class GetAllVideosUseCase(BaseVideoUseCase):
    async def execute(
        self: Self,
        offset: int = 0,
        limit: int = 20,
        user_id: str | None = None,
        *,
        include_deleted: bool = False,
    ) -> list[Video]:
        if user_id:
            return await self.repository.get_all_with_favorite_mark(
                user_id, offset, limit, include_deleted=include_deleted
            )
        return await self.repository.get_all(
            offset=offset,
            limit=limit,
            include_deleted=include_deleted,
        )


class GetCountVideosUseCase(BaseVideoUseCase):
    async def execute(self: Self) -> int:
        return await self.repository.count()


class GetVideoBySlugUseCase(BaseVideoUseCase):
    async def execute(self: Self, slug: str, user_id: str | None = None) -> Video:
        if user_id:
            return await self.repository.get_by_slug_with_favorite_mark(slug, user_id)
        return await self.repository.get_by_slug(slug)


class CreateVideoUseCase(AbstractFullTextVideoUseCase):
    async def execute(self: Self, new_video: NewVideoDto) -> Video:
        try:
            await self.repository.get_by_yt_id(new_video.yt_id)
            raise VideoYtIdNotUniqueError(new_video.yt_id)
        except VideoNotFoundError:
            pass

        try:
            if new_video.slug:
                await self.repository.get_by_slug(new_video.slug)
            new_video.expand_slug()
        except VideoNotFoundError:
            pass

        video = await self.repository.create(new_video)
        await self.full_text_repo.create(video)

        await self._set_permissions(video)

        return video

    async def _set_permissions(self: Self, video: Video) -> None:
        if self.permissions_repo is None:
            return

        resource = Object("video", video.slug)
        await self.permissions_repo.write(
            resource,
            "writer",
            Object("role", "admin"),
            "member",
        )
        await self.permissions_repo.write(
            resource,
            "reader",
            Object("user", "*"),
        )


class DeleteVideoUseCase(AbstractFullTextVideoUseCase):
    async def execute(
        self: Self,
        id_: int,
        type_: DeleteType = DeleteType.TEMPORARY,
    ) -> None:
        video = await self.repository.get_by_id(id_, include_deleted=True)

        # Handle permanent deletion of already soft-deleted videos
        if video.deleted and type_ == DeleteType.PERMANENT:
            await self.repository.delete(id_, type_=DeleteType.PERMANENT)
            await self.full_text_repo.delete(id_)
            await self._remove_permissions(video)
        elif video.deleted and type_ == DeleteType.TEMPORARY:
            # Video is already soft-deleted, cannot soft-delete again
            raise VideoAlreadyDeletedError
        else:
            await self.repository.delete(id_, type_=type_)
            await self.full_text_repo.delete(id_)
            await self._update_permissions_for_soft_delete(video)

    async def _update_permissions_for_soft_delete(self: Self, video: Video) -> None:
        """Update permissions for soft-deleted videos.

        Remove reader access but keep writer access.
        """
        if self.permissions_repo is None:
            return

        resource = Object("video", video.slug)
        await self.permissions_repo.delete(resource, "reader")

    async def _remove_permissions(self: Self, video: Video) -> None:
        """Remove all permissions for permanently deleted videos."""
        if self.permissions_repo is None:
            return

        resource = Object("video", video.slug)
        # Remove all permissions for permanent deletion
        await self.permissions_repo.delete(resource, "reader")
        await self.permissions_repo.delete(resource, "writer")


class RestoreVideoUseCase(AbstractFullTextVideoUseCase):
    async def execute(self: Self, id_: int) -> Video:
        video = await self.repository.restore(id_)

        await self.full_text_repo.restore(video)

        await self._restore_permissions(video)

        return video

    async def _restore_permissions(self: Self, video: Video) -> None:
        """Restore permissions for a restored video."""
        if self.permissions_repo is None:
            return

        resource = Object("video", video.slug)
        # Restore reader access for all users
        await self.permissions_repo.write(
            resource,
            "reader",
            Object("user", "*"),
        )


class UpdateVideoUseCase(AbstractFullTextVideoUseCase):
    async def execute(self: Self, updated_data: UpdateVideoDto) -> Video:
        video = await self.repository.get_by_slug(str(updated_data.slug))
        video = await self.repository.update(updated_data)
        await self.full_text_repo.update(video.id, updated_data)
        return video
