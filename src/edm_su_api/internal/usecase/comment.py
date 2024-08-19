from typing_extensions import Self

from edm_su_api.internal.entity.comment import Comment, NewCommentDto
from edm_su_api.internal.entity.video import Video
from edm_su_api.internal.usecase.repository.comment import (
    AbstractCommentRepository,
)


class BaseCommentUseCase:
    def __init__(
        self: Self,
        repository: AbstractCommentRepository,
    ) -> None:
        self.repository = repository


class CreateCommentUseCase(BaseCommentUseCase):
    async def execute(
        self: Self,
        new_comment: NewCommentDto,
    ) -> Comment:
        return await self.repository.create(new_comment)


class GetAllCommentsUseCase(BaseCommentUseCase):
    async def execute(
        self: Self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Comment]:
        return await self.repository.get_all(offset=offset, limit=limit)


class GetCountCommentsUseCase(BaseCommentUseCase):
    async def execute(self: Self) -> int:
        return await self.repository.count()


class GetVideoCommentsUseCase(BaseCommentUseCase):
    async def execute(
        self: Self,
        video: Video,
    ) -> list[Comment]:
        return await self.repository.get_video_comments(video.id)
