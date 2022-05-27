from pytest_mock import MockerFixture

from app import meilisearch
from app.settings import settings


def test_normalize_ms_index_name(mocker: MockerFixture) -> None:
    indexes = [
        {"name": "videos", "postfix": "", "full_name": "videos"},
        {"name": "videos", "postfix": "test", "full_name": "videos-test"},
    ]

    for index in indexes:
        mocker.patch.object(
            settings,
            "meilisearch_index_postfix",
            index["postfix"],
        )
        assert (
            meilisearch.normalize_ms_index_name(index["name"])
            == index["full_name"]
        )
