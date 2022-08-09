from abc import ABC

from app.internal.entity.video import Video
from app.internal.usecase.repository.video import AbstractVideoRepository


class BaseVideoUseCase(ABC):
    def __init__(self, repository: AbstractVideoRepository,) -> None:
        self.repository = repository


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
