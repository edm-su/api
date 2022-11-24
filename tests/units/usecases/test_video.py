from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pytest_mock import MockFixture

from app.internal.entity.video import NewVideoDto
from app.internal.usecase.exceptions.video import (
    NotFoundException,
    SlugNotUniqueException,
    VideoYtIdNotUniqueException,
)
from app.internal.usecase.repository.video import (
    AbstractFullTextVideoRepository,
    AbstractVideoRepository,
    MeilisearchVideoRepository,
    PostgresVideoRepository,
)
from app.internal.usecase.video import (
    CreateVideoUseCase,
    DeleteVideoUseCase,
    GetAllVideosUseCase,
    GetCountVideosUseCase,
    GetVideoBySlugUseCase,
    Video,
)


@pytest.fixture
def repository(mocker: MockFixture) -> PostgresVideoRepository:
    session = mocker.MagicMock()
    return PostgresVideoRepository(session)


@pytest.fixture
def full_text_repository(mocker: MockFixture) -> MeilisearchVideoRepository:
    client = mocker.MagicMock()
    return MeilisearchVideoRepository(client)


class TestGetAllVideosUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockFixture,
        faker: Faker,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.video"
            ".PostgresVideoRepository.get_all",
            return_value=[
                Video(
                    id=faker.pyint(),
                    slug=faker.slug(),
                    title=faker.sentence(),
                    date=faker.date_between(
                        start_date="-30d",
                        end_date="today",
                    ),
                    yt_id=faker.pystr(),
                    yt_thumbnail=faker.image_url(),
                    duration=faker.pyint(),
                )
                for _ in range(10)
            ],
        )

    @pytest.fixture
    def usecase(
        self,
        repository: AbstractVideoRepository,
    ) -> GetAllVideosUseCase:
        return GetAllVideosUseCase(repository)

    @pytest.mark.asyncio
    async def test_get_all_videos(
        self,
        usecase: GetAllVideosUseCase,
    ) -> None:
        videos = await usecase.execute()
        assert videos is not None
        assert len(videos) == 10

        usecase.repository.get_all: AsyncMock  # type: ignore
        usecase.repository.get_all.assert_awaited_once()  # type: ignore


class TestGetCountVideosUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockFixture,
        faker: Faker,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.video"
            ".PostgresVideoRepository.count",
            return_value=faker.pyint(),
        )

    @pytest.fixture
    def usecase(
        self,
        repository: AbstractVideoRepository,
    ) -> GetCountVideosUseCase:
        return GetCountVideosUseCase(repository)

    @pytest.mark.asyncio
    async def test_get_count_videos(
        self,
        usecase: GetCountVideosUseCase,
    ) -> None:
        count = await usecase.execute()
        assert count is not None
        assert count > 0

        usecase.repository.count: AsyncMock  # type: ignore
        usecase.repository.count.assert_awaited_once()  # type: ignore


class TestGetVideoBySlugUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockFixture,
        faker: Faker,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.video"
            ".PostgresVideoRepository.get_by_slug",
            return_value=Video(
                id=faker.pyint(),
                slug="slug",
                title=faker.sentence(),
                date=faker.date_between(
                    start_date="-30d",
                    end_date="today",
                ),
                yt_id=faker.pystr(),
                yt_thumbnail=faker.image_url(),
                duration=faker.pyint(),
            ),
        )

    @pytest.fixture
    def usecase(
        self,
        repository: AbstractVideoRepository,
    ) -> GetVideoBySlugUseCase:
        return GetVideoBySlugUseCase(repository)

    @pytest.mark.asyncio
    async def test_get_video_by_slug(
        self,
        usecase: GetVideoBySlugUseCase,
    ) -> None:
        video = await usecase.execute("slug")
        assert video is not None

        usecase.repository.get_by_slug: AsyncMock
        usecase.repository.get_by_slug.assert_awaited_once_with("slug")


class TestCreateVideoUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockFixture,
        new_video: NewVideoDto,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.video"
            ".PostgresVideoRepository.create",
            return_value=Video(
                id=1,
                **new_video.dict(),
            ),
        )
        mocker.patch(
            "app.internal.usecase.repository.video"
            ".MeilisearchVideoRepository.create",
            return_value=Video(
                id=1,
                **new_video.dict(),
            ),
        )

    @pytest.fixture
    def new_video(
        self,
        faker: Faker,
    ) -> NewVideoDto:
        return NewVideoDto(
            title=faker.pystr(),
            slug=faker.pystr(),
            duration=faker.pyint(),
            yt_id=faker.pystr(),
            yt_thumbnail=f"https://i.ytimg.com/vi/{faker.pystr()}"
            f"/default.jpg",
            date=faker.date_between(
                start_date="-1y",
                end_date="today",
            ),
        )

    @pytest.fixture
    def mock_by_slug(
        self,
        mocker: MockFixture,
        new_video: NewVideoDto,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.video"
            ".PostgresVideoRepository.get_by_slug",
            return_value=Video(
                id=1,
                **new_video.dict(),
            ),
        )

    @pytest.fixture
    def mock_by_yt_id(
        self,
        mocker: MockFixture,
        new_video: NewVideoDto,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.video"
            ".PostgresVideoRepository.get_by_yt_id",
            return_value=Video(
                id=1,
                **new_video.dict(),
            ),
        )

    @pytest.fixture
    def mock_not_found(
        self,
        mocker: MockFixture,
        new_video: NewVideoDto,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.video"
            ".PostgresVideoRepository.get_by_slug",
            return_value=None,
        )
        mocker.patch(
            "app.internal.usecase.repository.video"
            ".PostgresVideoRepository.get_by_yt_id",
            return_value=None,
        )

    @pytest.fixture
    def usecase(
        self,
        repository: AbstractVideoRepository,
        full_text_repository: AbstractFullTextVideoRepository,
    ) -> CreateVideoUseCase:
        return CreateVideoUseCase(repository, full_text_repository)

    @pytest.mark.asyncio
    async def test_create_video(
        self,
        usecase: CreateVideoUseCase,
        new_video: NewVideoDto,
        repository: AbstractVideoRepository,
        mock_not_found: None,
    ) -> None:
        video = await usecase.execute(new_video)
        assert video is not None
        assert video.title == new_video.title
        assert video.slug == new_video.slug
        assert video.duration == new_video.duration
        assert video.yt_id == new_video.yt_id
        assert video.yt_thumbnail == new_video.yt_thumbnail
        assert video.date == new_video.date

        usecase.repository.create: AsyncMock
        usecase.repository.create.assert_awaited_once_with(new_video)
        usecase.full_text_repo.create: AsyncMock
        usecase.full_text_repo.create.assert_awaited_once_with(video)

    @pytest.mark.asyncio
    async def test_create_video_with_invalid_slug(
        self,
        usecase: CreateVideoUseCase,
        faker: Faker,
        new_video: NewVideoDto,
        mock_by_slug: None,
    ) -> None:
        """Raise exception if slug is not unique."""
        with pytest.raises(SlugNotUniqueException):
            await usecase.execute(new_video)

    @pytest.mark.asyncio
    async def test_create_video_with_invalid_yt_id(
        self,
        usecase: CreateVideoUseCase,
        faker: Faker,
        new_video: NewVideoDto,
        mock_by_yt_id: None,
        mocker: MockFixture,
    ) -> None:
        """Raise exception if yt_id is not unique."""
        mocker.patch(
            "app.internal.usecase.repository.video"
            ".PostgresVideoRepository.get_by_slug",
            return_value=None,
        )
        with pytest.raises(VideoYtIdNotUniqueException):
            await usecase.execute(new_video)


class TestDeleteVideoUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.video"
            ".PostgresVideoRepository.delete",
            return_value=None,
        )
        mocker.patch(
            "app.internal.usecase.repository.video"
            ".MeilisearchVideoRepository.delete",
            return_value=None,
        )

    @pytest.fixture
    def usecase(
        self,
        repository: AbstractVideoRepository,
        full_text_repository: AbstractFullTextVideoRepository,
    ) -> DeleteVideoUseCase:
        return DeleteVideoUseCase(
            repository,
            full_text_repository,
        )

    @pytest.mark.asyncio
    async def test_delete_video(
        self,
        usecase: DeleteVideoUseCase,
        mocker: MockFixture,
        faker: Faker,
    ) -> None:
        video = Video(
            id=1,
            title=faker.pystr(),
            slug=faker.pystr(),
            duration=faker.pyint(),
            yt_id=faker.pystr(),
            yt_thumbnail=f"https://i.ytimg.com/vi/{faker.pystr()}"
            f"/default.jpg",
            date=faker.date_between(
                start_date="-1y",
                end_date="today",
            ),
        )
        mocker.patch(
            "app.internal.usecase.repository.video"
            ".PostgresVideoRepository.get_by_id",
            return_value=Video,
        )

        await usecase.execute(video.id)

        usecase.repository.delete: AsyncMock
        usecase.repository.delete.assert_awaited_once_with(video.id)
        usecase.full_text_repo.delete: AsyncMock
        usecase.full_text_repo.delete.assert_awaited_once_with(video.id)
        usecase.repository.get_by_id: AsyncMock
        usecase.repository.get_by_id.assert_awaited_once_with(video.id)

    @pytest.mark.asyncio
    async def test_delete_video_with_invalid_id(
        self,
        usecase: DeleteVideoUseCase,
        mocker: MockFixture,
    ) -> None:
        """Raise exception if id is not found."""
        mocker.patch(
            "app.internal.usecase.repository.video"
            ".PostgresVideoRepository.get_by_id",
            return_value=None,
        )
        with pytest.raises(NotFoundException):
            await usecase.execute(100_000_000)
        usecase.repository.get_by_id: AsyncMock
        usecase.repository.get_by_id.assert_awaited_once_with(100_000_000)
        usecase.repository.delete: AsyncMock
        usecase.repository.delete.assert_not_called()
