from typing_extensions import Self

from app.internal.entity.video import NewVideoDto, Video
from app.internal.usecase.exceptions.video import (
    VideoNotFoundError,
    VideoSlugNotUniqueError,
    VideoYtIdNotUniqueError,
)
from app.internal.usecase.repository.video import (
    AbstractFullTextVideoRepository,
    AbstractVideoRepository,
)


class BaseVideoUseCase:
    def __init__(
        self: Self,
        repository: AbstractVideoRepository,
    ) -> None:
        self.repository = repository


class AbstractFullTextVideoUseCase(BaseVideoUseCase):
    def __init__(
        self: Self,
        repository: AbstractVideoRepository,
        full_text_repo: AbstractFullTextVideoRepository,
    ) -> None:
        self.full_text_repo = full_text_repo
        super().__init__(repository)


class GetAllVideosUseCase(BaseVideoUseCase):
    async def execute(
        self: Self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Video]:
        return await self.repository.get_all(
            offset=offset,
            limit=limit,
        )


class GetCountVideosUseCase(BaseVideoUseCase):
    async def execute(self: Self) -> int:
        return await self.repository.count()


class GetVideoBySlugUseCase(BaseVideoUseCase):
    async def execute(self: Self, slug: str) -> Video:
        video = await self.repository.get_by_slug(slug)
        if video is None:
            raise VideoNotFoundError
        return video


class CreateVideoUseCase(AbstractFullTextVideoUseCase):
    async def execute(self: Self, new_video: NewVideoDto) -> Video:
        if await self.repository.get_by_slug(new_video.slug):  # type: ignore[arg-type]  # noqa: E501
            raise VideoSlugNotUniqueError(new_video.slug)  # type: ignore[arg-type]  # noqa: E501
        if await self.repository.get_by_yt_id(new_video.yt_id):
            raise VideoYtIdNotUniqueError(new_video.yt_id)
        video = await self.repository.create(new_video)
        await self.full_text_repo.create(video)
        return video


class DeleteVideoUseCase(AbstractFullTextVideoUseCase):
    async def execute(self: Self, id_: int) -> None:
        video = await self.repository.get_by_id(id_)
        if not video:
            raise VideoNotFoundError
        await self.repository.delete(id_)
        await self.full_text_repo.delete(id_)
