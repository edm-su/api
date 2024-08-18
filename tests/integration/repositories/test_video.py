import pytest
from faker import Faker
from meilisearch_python_async import Client
from meilisearch_python_async.errors import MeilisearchApiError
from typing_extensions import Self

from app.internal.entity.video import NewVideoDto, Video
from app.internal.usecase.exceptions.video import VideoNotFoundError
from app.internal.usecase.repository.video import (
    MeilisearchVideoRepository,
    PostgresVideoRepository,
)


class TestPostgresVideoRepository:
    @pytest.fixture
    def new_video_data(
        self: Self,
        faker: Faker,
    ) -> NewVideoDto:
        return NewVideoDto(
            title=faker.word(),
            date=faker.date(),
            yt_id=faker.uuid4(),
            yt_thumbnail=faker.url(),
            duration=faker.random_int(
                min=20 * 60,
                max=120 * 60,
            ),
            slug=faker.slug(),
        )

    async def test_get_all(
        self: Self,
        pg_video: Video,
        pg_video_repository: PostgresVideoRepository,
    ) -> None:
        result = await pg_video_repository.get_all()

        assert isinstance(result, list)
        assert len(result) > 0
        assert pg_video in result

    async def test_get_by_slug(
        self: Self,
        pg_video: Video,
        pg_video_repository: PostgresVideoRepository,
    ) -> None:
        result = await pg_video_repository.get_by_slug(pg_video.slug)

        assert result == pg_video

    async def test_get_by_yt_id(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        pg_video: Video,
    ) -> None:
        result = await pg_video_repository.get_by_yt_id(pg_video.yt_id)

        assert result == pg_video

    async def test_get_by_id(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        pg_video: Video,
    ) -> None:
        result = await pg_video_repository.get_by_id(pg_video.id)

        assert result == pg_video

    async def test_create(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        new_video_data: NewVideoDto,
    ) -> None:
        result = await pg_video_repository.create(new_video_data)

        assert isinstance(result, Video)

        pg_video = await pg_video_repository.get_by_id(result.id)

        assert pg_video == result

    async def test_update(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        pg_video: Video,
    ) -> None:
        pg_video.title = "new title"
        result = await pg_video_repository.update(pg_video)

        assert result == pg_video

        video = await pg_video_repository.get_by_id(result.id)

        assert video == result

    async def test_delete(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        pg_video: Video,
    ) -> None:
        await pg_video_repository.delete(pg_video.id)

        with pytest.raises(VideoNotFoundError):
            await pg_video_repository.get_by_id(pg_video.id)

    async def test_count(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        pg_video: Video,
    ) -> None:
        result = await pg_video_repository.count()

        assert result > 0


class TestMeilisearchVideoRepository:
    @pytest.fixture(scope="session")
    def repository(
        self: Self,
        ms_client: Client,
    ) -> MeilisearchVideoRepository:
        return MeilisearchVideoRepository(ms_client)

    @pytest.fixture
    async def ms_video(
        self: Self,
        repository: MeilisearchVideoRepository,
        pg_video: Video,
    ) -> Video:
        return await repository.create(pg_video)

    async def test_create(
        self: Self,
        pg_video: Video,
        repository: MeilisearchVideoRepository,
    ) -> None:
        result = await repository.create(pg_video)

        assert isinstance(result, Video)
        assert await repository.index.get_document(str(result.id))

    async def test_delete(
        self: Self,
        ms_video: Video,
        repository: MeilisearchVideoRepository,
    ) -> None:
        await repository.delete(ms_video.id)

        with pytest.raises(MeilisearchApiError):
            await repository.index.get_document(str(ms_video.id))
