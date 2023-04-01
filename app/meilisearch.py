from typing import Self

from meilisearch_python_async import Client as MeilisearchClient
from meilisearch_python_async.index import Index
from meilisearch_python_async.models.task import TaskId

from app.settings import settings


class MeilisearchRepository:
    client = MeilisearchClient(
        url=settings.meilisearch_api_url,
        api_key=settings.meilisearch_api_key,
    )

    async def close(self: Self) -> None:
        await self.client.aclose()

    @staticmethod
    async def clear_index(index: Index) -> TaskId:
        return await index.delete_all_documents()

    async def indexes(self: Self) -> list[Index] | None:
        return await self.client.get_indexes()

    async def get_index(self: Self, index_name: str) -> Index:
        return await self.client.get_or_create_index(index_name)

    @staticmethod
    def normalize_index_name(index_name: str) -> str:
        postfix = settings.meilisearch_index_postfix
        if postfix:
            return f"{index_name}-{postfix}"
        return index_name


meilisearch_client = MeilisearchRepository()
