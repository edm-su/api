from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pytest_mock import MockFixture
from pytest_mock.plugin import MockType
from typing_extensions import Self

from edm_su_api.internal.entity.video import NewVideoDto, UpdateVideoDto
from edm_su_api.internal.usecase.exceptions.video import (
    VideoNotFoundError,
    VideoYtIdNotUniqueError,
)
from edm_su_api.internal.usecase.repository.video import (
    AbstractFullTextVideoRepository,
    AbstractVideoRepository,
)
from edm_su_api.internal.usecase.video import (
    CreateVideoUseCase,
    DeleteVideoUseCase,
    GetAllVideosUseCase,
    GetCountVideosUseCase,
    GetVideoBySlugUseCase,
    UpdateVideoUseCase,
    Video,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def repository(mocker: MockFixture) -> AsyncMock:
    return mocker.AsyncMock(spec=AbstractVideoRepository)


@pytest.fixture
def full_text_repository(mocker: MockFixture) -> AsyncMock:
    return mocker.AsyncMock(spec=AbstractFullTextVideoRepository)


@pytest.fixture
def video(faker: Faker) -> Video:
    return Video(
        id=faker.pyint(min_value=1),
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
    def mock(
        self: Self,
        repository: AsyncMock,
        video: Video,
    ) -> None:
        repository.get_all.return_value = [video]

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetAllVideosUseCase:
        return GetAllVideosUseCase(repository)

    async def test_get_all_videos(
        self: Self,
        usecase: GetAllVideosUseCase,
        repository: AsyncMock,
    ) -> None:
        videos = await usecase.execute()
        assert videos is not None
        assert len(videos) == 1

        repository.get_all.assert_awaited_once_with(offset=0, limit=20)

    async def test_get_all_videos_with_user_id(
        self: Self,
        usecase: GetAllVideosUseCase,
        repository: AsyncMock,
        video: Video,
    ) -> None:
        """Test getting all videos with user_id parameter."""
        repository.get_all_with_favorite_mark.return_value = [video]

        videos = await usecase.execute(user_id="test_user_id")
        assert videos is not None
        assert len(videos) == 1

        repository.get_all_with_favorite_mark.assert_awaited_once_with(
            "test_user_id",
            0,
            20,
        )


class TestGetCountVideosUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        repository.count.return_value = 1

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetCountVideosUseCase:
        return GetCountVideosUseCase(repository)

    async def test_get_count_videos(
        self: Self,
        usecase: GetCountVideosUseCase,
        repository: AsyncMock,
    ) -> None:
        count = await usecase.execute()
        assert count == 1

        repository.count.assert_awaited_once()


class TestGetVideoBySlugUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self: Self,
        repository: AsyncMock,
        video: Video,
    ) -> None:
        repository.get_by_slug.return_value = video

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetVideoBySlugUseCase:
        return GetVideoBySlugUseCase(repository)

    async def test_get_video_by_slug(
        self: Self,
        usecase: GetVideoBySlugUseCase,
        video: Video,
        repository: AsyncMock,
    ) -> None:
        db_video = await usecase.execute("slug")
        assert db_video is video

        repository.get_by_slug.assert_awaited_once_with("slug")

    async def test_get_video_by_slug_with_user_id(
        self: Self,
        usecase: GetVideoBySlugUseCase,
        video: Video,
        repository: AsyncMock,
    ) -> None:
        """Test getting video by slug with user_id parameter."""
        repository.get_by_slug_with_favorite_mark.return_value = video

        db_video = await usecase.execute("slug", user_id="test_user_id")
        assert db_video is video

        repository.get_by_slug_with_favorite_mark.assert_awaited_once_with(
            "slug",
            "test_user_id",
        )

    async def test_video_not_found_error(
        self: Self,
        usecase: GetVideoBySlugUseCase,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_slug.side_effect = VideoNotFoundError
        with pytest.raises(VideoNotFoundError):
            await usecase.execute("slug")
        repository.get_by_slug.assert_awaited_once_with("slug")


class TestCreateVideoUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self: Self,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
        video: Video,
    ) -> None:
        repository.create.return_value = video
        full_text_repository.create.return_value = video

    @pytest.fixture
    def new_video(
        self: Self,
        video: Video,
    ) -> NewVideoDto:
        return NewVideoDto(**video.model_dump())

    @pytest.fixture
    def mock_by_slug(
        self: Self,
        repository: AsyncMock,
        video: Video,
    ) -> None:
        repository.get_by_slug.return_value = video

    @pytest.fixture
    def mock_by_yt_id(
        self: Self,
        repository: AsyncMock,
        video: Video,
    ) -> None:
        repository.get_by_yt_id.return_value = video

    @pytest.fixture
    def mock_not_found(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_slug.side_effect = VideoNotFoundError
        repository.get_by_yt_id.side_effect = VideoNotFoundError

    @pytest.fixture
    def expand_slug_patch(self: Self, mocker: MockFixture) -> MockType:
        return mocker.patch.object(NewVideoDto, "expand_slug", return_value="")

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
        permissions_repo: AsyncMock,
    ) -> CreateVideoUseCase:
        return CreateVideoUseCase(
            repository,
            full_text_repository,
            permissions_repo,
        )

    @pytest.mark.usefixtures("mock_not_found")
    async def test_create_video(
        self: Self,
        usecase: CreateVideoUseCase,
        new_video: NewVideoDto,
        video: Video,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
        expand_slug_patch: MockType,
    ) -> None:
        created_video = await usecase.execute(new_video)
        assert created_video is video

        repository.create.assert_awaited_once_with(new_video)
        full_text_repository.create.assert_awaited_once_with(created_video)
        repository.get_by_slug.assert_awaited_once_with(video.slug)
        repository.get_by_yt_id.assert_awaited_once_with(video.yt_id)
        expand_slug_patch.assert_not_called()

    async def test_create_video_with_already_existing_slug(
        self: Self,
        usecase: CreateVideoUseCase,
        new_video: NewVideoDto,
        repository: AsyncMock,
        expand_slug_patch: MockType,
    ) -> None:
        """Raise exception if slug is not unique."""
        repository.get_by_yt_id.side_effect = VideoNotFoundError

        await usecase.execute(new_video)

        expand_slug_patch.assert_called_once()

    @pytest.mark.usefixtures("mock_by_yt_id")
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


class TestUpdateVideoUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self: Self,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
        video: Video,
    ) -> None:
        repository.update.return_value = video

    @pytest.fixture
    def update_video(
        self: Self,
        video: Video,
    ) -> UpdateVideoDto:
        return UpdateVideoDto(
            title=video.title,
            date=video.date,
            slug=video.slug,
        )

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
    ) -> UpdateVideoUseCase:
        return UpdateVideoUseCase(repository, full_text_repository)

    async def test_update_video(
        self: Self,
        usecase: UpdateVideoUseCase,
        update_video: UpdateVideoDto,
        video: Video,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
    ) -> None:
        result = await usecase.execute(update_video)
        assert result == video

        repository.update.assert_awaited_once_with(update_video)
        full_text_repository.update.assert_awaited_once_with(video.id, update_video)
        repository.get_by_slug.assert_awaited_once_with(update_video.slug)

    async def test_update_video_dont_exist(
        self: Self,
        usecase: UpdateVideoUseCase,
        update_video: UpdateVideoDto,
        video: Video,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
    ) -> None:
        repository.get_by_slug.side_effect = VideoNotFoundError

        with pytest.raises(VideoNotFoundError):
            await usecase.execute(update_video)


class TestDeleteVideoUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self: Self,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
    ) -> None:
        repository.delete.return_value = None
        full_text_repository.delete.return_value = None

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
        permissions_repo: AsyncMock,
    ) -> DeleteVideoUseCase:
        return DeleteVideoUseCase(
            repository,
            full_text_repository,
            permissions_repo,
        )

    async def test_delete_video(
        self: Self,
        usecase: DeleteVideoUseCase,
        repository: AsyncMock,
        video: Video,
        full_text_repository: AsyncMock,
    ) -> None:
        repository.get_by_id.return_value = video

        await usecase.execute(video.id)

        repository.delete.assert_awaited_once_with(video.id)
        full_text_repository.delete.assert_awaited_once_with(video.id)
        repository.get_by_id.assert_awaited_once_with(video.id)

    async def test_delete_video_with_invalid_id(
        self: Self,
        usecase: DeleteVideoUseCase,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
    ) -> None:
        repository.get_by_id.side_effect = VideoNotFoundError

        with pytest.raises(VideoNotFoundError):
            await usecase.execute(100_000_000)

        repository.get_by_id.assert_awaited_once_with(100_000_000)
        repository.delete.assert_not_called()
        full_text_repository.delete.assert_not_called()
