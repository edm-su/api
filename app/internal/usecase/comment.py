from abc import ABC

from app.internal.entity.comment import Comment, NewCommentDto
from app.internal.usecase.repository.comment import AbstractCommentRepository


class BaseCommentUseCase(ABC):
    def __init__(self, repository: AbstractCommentRepository) -> None:
        self.repository = repository


class CreateCommentUseCase(BaseCommentUseCase):
    async def execute(self, new_comment: NewCommentDto) -> Comment:
        return await self.repository.create(new_comment)


class GetAllCommentsUseCase(BaseCommentUseCase):
    async def execute(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Comment]:
        return await self.repository.get_all(offset=offset, limit=limit)


class GetCountCommentsUseCase(BaseCommentUseCase):
    async def execute(self) -> int:
        return await self.repository.count()


class GetVideoCommentsUseCase(BaseCommentUseCase):
    async def execute(
        self,
        video_id: int,
    ) -> list[Comment]:
        return await self.repository.get_video_comments(video_id)
