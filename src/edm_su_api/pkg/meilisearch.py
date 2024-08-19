from meilisearch_python_async import Client as MeilisearchClient
from meilisearch_python_async.models.settings import MeilisearchSettings
from meilisearch_python_async.task import wait_for_task

from edm_su_api.internal.entity.settings import settings

ms_client = MeilisearchClient(
    url=settings.meilisearch_api_url,
    api_key=settings.meilisearch_api_key,
)


def normalize_ms_index_name(index_name: str) -> str:
    postfix = settings.meilisearch_index_postfix
    if postfix:
        return f"{index_name}-{postfix}"
    return index_name


async def config_ms(client: MeilisearchClient) -> None:
    video_index = await client.create_index(
        normalize_ms_index_name("videos"),
        "id",
    )
    video_index_settings = MeilisearchSettings(
        sortable_attributes=["date", "title"],
        ranking_rules=[
            "sort",
            "words",
            "typo",
            "proximity",
            "attribute",
            "exactness",
        ],
        filterable_attributes=["slug", "yt_id"],
    )
    task = await video_index.update_settings(video_index_settings)
    await wait_for_task(ms_client.http_client, task.task_uid)
