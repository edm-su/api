import logging
from abc import ABC

from app.internal.entity.video import (
    Video,
    NewVideoDto,
)
from app.internal.usecase.exceptions.video import (
    VideoSlugNotUniqueException,
    VideoYtIdNotUniqueException,
    VideoNotFoundException,
)
from app.internal.usecase.repository.video import (
    AbstractVideoRepository,
    AbstractFullTextVideoRepository,
)


class BaseVideoUseCase(ABC):
    def __init__(
        self,
        repository: AbstractVideoRepository,
    ) -> None:
        self.repository = repository


class AbstractFullTextVideoUseCase(BaseVideoUseCase):
    def __init__(
        self,
        repository: AbstractVideoRepository,
        full_text_repo: AbstractFullTextVideoRepository,
    ) -> None:
        self.full_text_repo = full_text_repo
        super().__init__(repository)


class GetAllVideosUseCase(BaseVideoUseCase):
    async def execute(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Video]:
        return await self.repository.get_all(
            offset=offset,
            limit=limit,
        )


class GetCountVideosUseCase(BaseVideoUseCase):
    async def execute(self) -> int:
        return await self.repository.count()


class GetVideoBySlugUseCase(BaseVideoUseCase):
    async def execute(self, slug: str) -> Video | None:
        video = await self.repository.get_by_slug(slug)
        if video is None:
            raise VideoNotFoundException()
        return video


class CreateVideoUseCase(AbstractFullTextVideoUseCase):
    async def execute(self, new_video: NewVideoDto) -> Video:
        if await self.repository.get_by_slug(new_video.slug):
            raise VideoSlugNotUniqueException(new_video.slug)
        if await self.repository.get_by_yt_id(new_video.yt_id):
            raise VideoYtIdNotUniqueException(new_video.yt_id)
        video = await self.repository.create(new_video)
        await self.full_text_repo.create(video)
        return video


class DeleteVideoUseCase(AbstractFullTextVideoUseCase):
    async def execute(self, id_: int) -> None:
        video = await self.repository.get_by_id(id_)
        if not video:
            raise VideoNotFoundException()
        await self.repository.delete(
            id_
        )
        try:
            await self.full_text_repo.delete(id_)
        except Exception as e:
            logging.getLogger("app").error(e)
