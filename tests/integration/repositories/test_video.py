import pytest
from faker import Faker
from meilisearch_python_async import Client
from meilisearch_python_async.errors import MeilisearchApiError
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from edm_su_api.internal.entity.user import User
from edm_su_api.internal.entity.video import NewVideoDto, Video
from edm_su_api.internal.usecase.exceptions.video import VideoNotFoundError
from edm_su_api.internal.usecase.repository.user_videos import (
    PostgresUserVideosRepository,
)
from edm_su_api.internal.usecase.repository.video import (
    MeilisearchVideoRepository,
    PostgresVideoRepository,
)

pytestmark = pytest.mark.anyio


class TestPostgresVideoRepository:
    @pytest.fixture
    def user_videos_repository(
        self, pg_session: AsyncSession
    ) -> PostgresUserVideosRepository:
        return PostgresUserVideosRepository(pg_session)

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

    async def test_get_all_with_favorite_mark(
        self: Self,
        pg_video: Video,
        pg_video_repository: PostgresVideoRepository,
        user: User,
        user_videos_repository: PostgresUserVideosRepository,
    ) -> None:
        await user_videos_repository.like_video(user, pg_video)

        result = await pg_video_repository.get_all_with_favorite_mark(user.id)

        assert isinstance(result, list)
        assert len(result) > 0

        video = result[0]
        assert video.id == pg_video.id
        assert video.is_favorite is True

    async def test_get_by_slug_with_favorite_mark(
        self: Self,
        pg_video: Video,
        pg_video_repository: PostgresVideoRepository,
        user: User,
        user_videos_repository: PostgresUserVideosRepository,
    ) -> None:
        await user_videos_repository.like_video(user, pg_video)

        result = await pg_video_repository.get_by_slug_with_favorite_mark(
            pg_video.slug, user.id
        )

        assert isinstance(result, Video)
        assert result.id == pg_video.id
        assert result.is_favorite is True

        await user_videos_repository.unlike_video(user, pg_video)
        result = await pg_video_repository.get_by_slug_with_favorite_mark(
            pg_video.slug, user.id
        )

        assert result.is_favorite is False

        with pytest.raises(VideoNotFoundError):
            await pg_video_repository.get_by_slug_with_favorite_mark("9999", user.id)

    @pytest.mark.usefixtures("pg_video")
    async def test_count(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
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
