from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pytest_mock import MockFixture
from typing_extensions import Self

from app.internal.entity.video import NewVideoDto
from app.internal.usecase.exceptions.video import (
    NotFoundError,
    SlugNotUniqueError,
    VideoYtIdNotUniqueError,
)
from app.internal.usecase.repository.video import (
    AbstractFullTextVideoRepository,
    AbstractVideoRepository,
)
from app.internal.usecase.video import (
    CreateVideoUseCase,
    DeleteVideoUseCase,
    GetAllVideosUseCase,
    GetCountVideosUseCase,
    GetVideoBySlugUseCase,
    Video,
)


@pytest.fixture()
def repository(mocker: MockFixture) -> AsyncMock:
    return mocker.AsyncMock(spec=AbstractVideoRepository)


@pytest.fixture()
def full_text_repository(mocker: MockFixture) -> AsyncMock:
    return mocker.AsyncMock(spec=AbstractFullTextVideoRepository)

@pytest.fixture()
def video(faker: Faker) -> Video:
    return Video(
        id=faker.pyint(),
        slug=faker.pystr(),
        title=faker.sentence(),
        date=faker.date_between(
            start_date="-30d",
            end_date="today",
        ),
        yt_id=faker.pystr(),
        yt_thumbnail=faker.image_url(),
        duration=faker.pyint(),
    )


class TestGetAllVideosUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
        video: Video,
    ) -> None:
        repository.get_all.return_value = [video]

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetAllVideosUseCase:
        return GetAllVideosUseCase(repository)

    @pytest.mark.asyncio()
    async def test_get_all_videos(
        self: Self,
        usecase: GetAllVideosUseCase,
    ) -> None:
        videos = await usecase.execute()
        assert videos is not None
        assert len(videos) == 1

        usecase.repository.get_all.assert_awaited_once_with(offset=0, limit=20)  # type: ignore[attr-defined]  # noqa: E501


class TestGetCountVideosUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        repository.count.return_value = 1

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetCountVideosUseCase:
        return GetCountVideosUseCase(repository)

    @pytest.mark.asyncio()
    async def test_get_count_videos(
        self: Self,
        usecase: GetCountVideosUseCase,
    ) -> None:
        count = await usecase.execute()
        assert count == 1

        usecase.repository.count.assert_awaited_once()  # type: ignore[attr-defined]  # noqa: E501


class TestGetVideoBySlugUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
        video: Video,
    ) -> None:
        repository.get_by_slug.return_value = video

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetVideoBySlugUseCase:
        return GetVideoBySlugUseCase(repository)

    @pytest.mark.asyncio()
    async def test_get_video_by_slug(
        self: Self,
        usecase: GetVideoBySlugUseCase,
        video: Video,
    ) -> None:
        video = await usecase.execute("slug")
        assert video is video

        usecase.repository.get_by_slug.assert_awaited_once_with("slug")  # type: ignore[attr-defined]  # noqa: E501


class TestCreateVideoUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
        video: Video,
    ) -> None:
        repository.create.return_value = video
        full_text_repository.create.return_value = video

    @pytest.fixture()
    def new_video(
        self: Self,
        video: Video,
    ) -> NewVideoDto:
        return NewVideoDto(**video.dict())

    @pytest.fixture()
    def _mock_by_slug(
        self: Self,
        repository: AsyncMock,
        video: Video,
    ) -> None:
        repository.get_by_slug.return_value = video

    @pytest.fixture()
    def _mock_by_yt_id(
        self: Self,
        repository: AsyncMock,
        video: Video,
    ) -> None:
        repository.get_by_yt_id.return_value = video

    @pytest.fixture()
    def _mock_not_found(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_slug.return_value = None
        repository.get_by_yt_id.return_value = None

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
    ) -> CreateVideoUseCase:
        return CreateVideoUseCase(repository, full_text_repository)

    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("_mock_not_found")
    async def test_create_video(
        self: Self,
        usecase: CreateVideoUseCase,
        new_video: NewVideoDto,
        video: Video,
    ) -> None:
        created_video = await usecase.execute(new_video)
        assert created_video is video

        usecase.repository.create.assert_awaited_once_with(new_video)  # type: ignore[attr-defined]  # noqa: E501
        usecase.full_text_repo.create.assert_awaited_once_with(created_video)  # type: ignore[attr-defined]  # noqa: E501
        usecase.repository.get_by_slug.assert_awaited_once_with(video.slug)  # type: ignore[attr-defined]  # noqa: E501
        usecase.repository.get_by_yt_id.assert_awaited_once_with(video.yt_id)  # type: ignore[attr-defined]  # noqa: E501

    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("_mock_by_slug")
    async def test_create_video_with_invalid_slug(
        self: Self,
        usecase: CreateVideoUseCase,
        new_video: NewVideoDto,
    ) -> None:
        """Raise exception if slug is not unique."""
        with pytest.raises(SlugNotUniqueError):
            await usecase.execute(new_video)

    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("_mock_by_yt_id")
    async def test_create_video_with_invalid_yt_id(
        self: Self,
        repository: AsyncMock,
        new_video: NewVideoDto,
        usecase: CreateVideoUseCase,
    ) -> None:
        """Raise exception if yt_id is not unique."""
        repository.get_by_slug.return_value = None
        with pytest.raises(VideoYtIdNotUniqueError):
            await usecase.execute(new_video)


class TestDeleteVideoUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
    ) -> None:
        repository.delete.return_value = None
        full_text_repository.delete.return_value = None

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
    ) -> DeleteVideoUseCase:
        return DeleteVideoUseCase(
            repository,
            full_text_repository,
        )

    @pytest.mark.asyncio()
    async def test_delete_video(
        self: Self,
        usecase: DeleteVideoUseCase,
        repository: AsyncMock,
        video: Video,
    ) -> None:
        repository.get_by_id.return_value = video

        await usecase.execute(video.id)

        usecase.repository.delete.assert_awaited_once_with(video.id)  # type: ignore[attr-defined]  # noqa: E501
        usecase.full_text_repo.delete.assert_awaited_once_with(video.id)  # type: ignore[attr-defined]  # noqa: E501
        usecase.repository.get_by_id.assert_awaited_once_with(video.id)  # type: ignore[attr-defined]  # noqa: E501

    @pytest.mark.asyncio()
    async def test_delete_video_with_invalid_id(
        self: Self,
        usecase: DeleteVideoUseCase,
        repository: AsyncMock,
    ) -> None:
        """Raise exception if id is not found."""
        repository.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            await usecase.execute(100_000_000)

        usecase.repository.get_by_id.assert_awaited_once_with(100_000_000)  # type: ignore[attr-defined]  # noqa: E501
        usecase.repository.delete.assert_not_called()  # type: ignore[attr-defined]  # noqa: E501
        usecase.full_text_repo.delete.assert_not_called()  # type: ignore[attr-defined]  # noqa: E501
