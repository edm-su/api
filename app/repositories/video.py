from abc import ABC, abstractmethod
from typing import Any

from fastapi.encoders import jsonable_encoder
from meilisearch_python_async.models.task import TaskInfo
from pydantic import parse_obj_as
from typing_extensions import Self

from app.meilisearch import MeilisearchRepository
from app.schemas.video import MeilisearchVideo


class VideoRepository(ABC):
    @abstractmethod
    def create(self: Self, video: Any) -> Any:  # noqa: ANN401
        pass

    @abstractmethod
    def delete(self: Self, id_: int) -> Any:  # noqa: ANN401
        pass

    @abstractmethod
    def get_all(
        self: Self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Any | None]:
        pass

    @abstractmethod
    def get_by_id(self: Self, id_: int) -> Any:  # noqa: ANN401
        pass

    @abstractmethod
    def update(self: Self, video: Any) -> Any:  # noqa: ANN401
        pass

    @abstractmethod
    def delete_all(self: Self) -> Any:  # noqa: ANN401
        pass


class MeilisearchVideoRepository(VideoRepository, MeilisearchRepository):
    def __init__(self: Self) -> None:
        index_name = self.normalize_index_name("videos")
        self.index = self.client.index(index_name)

    async def create(self: Self, video: MeilisearchVideo) -> TaskInfo:
        documents = [jsonable_encoder(video)]
        return await self.index.add_documents(documents)

    async def delete(self: Self, id_: int) -> TaskInfo:
        return await self.index.delete_document(str(id_))

    async def get_all(  # type: ignore[override]
        self: Self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MeilisearchVideo | None]:
        documents = await self.index.get_documents(limit=limit, offset=offset)
        if documents.total > 0:
            return parse_obj_as(
                list[MeilisearchVideo | None],
                documents.results,
            )
        return []

    async def get_by_id(self: Self, id_: int) -> MeilisearchVideo:
        document = await self.index.get_document(str(id_))
        return MeilisearchVideo.parse_obj(document)

    async def update(
        self: Self,
        video: MeilisearchVideo,
    ) -> TaskInfo:
        return await self.create(video)

    async def delete_all(self: Self) -> TaskInfo:
        return await self.clear_index(self.index)


meilisearch_video_repository = MeilisearchVideoRepository()
