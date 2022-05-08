import meilisearch_python_async
import pytest
from meilisearch_python_async.task import wait_for_task
from pytest_mock import MockerFixture

from app.meilisearch import MeilisearchRepository, meilisearch_client
from app.repositories.video import meilisearch_video_repository
from app.schemas.video import MeilisearchVideo
from app.settings import settings


class TestMeilisearchRepository:
    def test_normalize_index_name(self) -> None:
        index_name = MeilisearchRepository._normalize_index_name('index')
        assert index_name == f'index-{settings.meilisearch_index_postfix}'

        settings.meilisearch_index_postfix = ''
        index_name = MeilisearchRepository._normalize_index_name('index')
        assert index_name == 'index'

    @pytest.mark.asyncio
    async def test_close(self, mocker: MockerFixture) -> None:
        mocker.patch('meilisearch_python_async.Client.aclose')
        await meilisearch_client.close()
        meilisearch_python_async.Client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_index(self, ms_video: MeilisearchVideo) -> None:
        index = meilisearch_video_repository.index
        task = await meilisearch_client.clear_index(index)
        await wait_for_task(
            meilisearch_client.client.http_client,
            task.uid,
        )

        assert await meilisearch_video_repository.get_all() == []

    @pytest.mark.asyncio
    async def test_indexes(self, ms_video: MeilisearchVideo) -> None:
        index_name = meilisearch_video_repository.index.uid
        indexes = await meilisearch_client.indexes()
        assert index_name in [index.uid for index in indexes]
