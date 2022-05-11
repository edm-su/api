from abc import ABC, abstractmethod
from typing import Any

from fastapi.encoders import jsonable_encoder
from meilisearch_python_async.models.task import TaskId
from pydantic import parse_obj_as

from app.meilisearch import MeilisearchRepository
from app.schemas.video import MeilisearchVideo


class VideoRepository(ABC):
    @abstractmethod
    def create(self, video: Any) -> Any:
        pass

    @abstractmethod
    def delete(self, id_: int) -> Any:
        pass

    @abstractmethod
    def get_all(self, *, limit: int = 20, offset: int = 0) -> list[Any | None]:
        pass

    @abstractmethod
    def get_by_id(self, id_: int) -> Any:
        pass

    @abstractmethod
    def update(self, video: Any) -> Any:
        pass

    @abstractmethod
    def delete_all(self) -> Any:
        pass


class MeilisearchVideoRepository(VideoRepository, MeilisearchRepository):
    def __init__(self) -> None:
        index_name = self._normalize_index_name("videos")
        self.index = self.client.index(index_name)

    async def create(
            self,
            video: MeilisearchVideo
    ) -> TaskId:
        documents = [jsonable_encoder(video)]
        return await self.index.add_documents(documents)

    async def delete(self, id_: int) -> TaskId:
        return await self.index.delete_document(str(id_))

    async def get_all(  # type: ignore[override]
            self,
            *,
            limit: int = 20,
            offset: int = 0
    ) -> list[MeilisearchVideo | None]:
        documents = await self.index.get_documents(limit=limit, offset=offset)
        if documents:
            return parse_obj_as(
                list[MeilisearchVideo],  # type: ignore
                documents
            )
        return []

    async def get_by_id(self, id_: int) -> MeilisearchVideo:
        document = await self.index.get_document(str(id_))
        return MeilisearchVideo.parse_obj(document)

    async def update(
            self,
            video: MeilisearchVideo,
    ) -> TaskId:
        return await self.create(video)

    async def delete_all(self) -> TaskId:
        return await self.clear_index(self.index)


meilisearch_video_repository = MeilisearchVideoRepository()
