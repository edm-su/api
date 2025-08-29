from typing_extensions import Self

from edm_su_api.internal.entity.video import NewVideoDto, UpdateVideoDto, Video
from edm_su_api.internal.usecase.exceptions.video import (
    VideoNotFoundError,
    VideoYtIdNotUniqueError,
)
from edm_su_api.internal.usecase.repository.permission import (
    AbstractPermissionRepository,
    Object,
)
from edm_su_api.internal.usecase.repository.video import (
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


class GetAllVideosUseCase(BaseVideoUseCase):
    async def execute(
        self: Self,
        offset: int = 0,
        limit: int = 20,
        user_id: str | None = None,
    ) -> list[Video]:
        if user_id:
            await self.repository.get_all_with_favorite_mark(user_id, offset, limit)
        return await self.repository.get_all(
            offset=offset,
            limit=limit,
        )


class GetCountVideosUseCase(BaseVideoUseCase):
    async def execute(self: Self) -> int:
        return await self.repository.count()


class GetVideoBySlugUseCase(BaseVideoUseCase):
    async def execute(self: Self, slug: str, user_id: str | None = None) -> Video:
        if user_id:
            return await self.repository.get_by_slug_with_favorite_mark(slug, user_id)
        return await self.repository.get_by_slug(slug)


class CreateVideoUseCase(BaseVideoUseCase):
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


class DeleteVideoUseCase(BaseVideoUseCase):
    async def execute(self: Self, id_: int) -> None:
        video = await self.repository.get_by_id(id_)
        await self.repository.delete(id_)
        await self._set_permissions(video)

    async def _set_permissions(self: Self, video: Video) -> None:
        if self.permissions_repo is None:
            return

        resource = Object("video", video.slug)
        await self.permissions_repo.delete(resource, "reader")


class UpdateVideoUseCase(BaseVideoUseCase):
    async def execute(self: Self, updated_data: UpdateVideoDto) -> Video:
        await self.repository.get_by_slug(str(updated_data.slug))
        return await self.repository.update(updated_data)
