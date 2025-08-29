from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pytest_mock import MockFixture
from pytest_mock.plugin import MockType
from typing_extensions import Self

from edm_su_api.internal.entity.video import DeleteType, NewVideoDto, UpdateVideoDto
from edm_su_api.internal.usecase.exceptions.video import (
    VideoAlreadyDeletedError,
    VideoNotDeletedError,
    VideoNotFoundError,
    VideoYtIdNotUniqueError,
)
from edm_su_api.internal.usecase.repository.permission import Object
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
    RestoreVideoUseCase,
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
def permissions_repo(mocker: MockFixture) -> AsyncMock:
    return mocker.AsyncMock()


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

        repository.get_all.assert_awaited_once_with(
            offset=0, limit=20, include_deleted=False
        )

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
            include_deleted=False,
        )

    async def test_get_all_videos_with_include_deleted(
        self: Self,
        usecase: GetAllVideosUseCase,
        repository: AsyncMock,
    ) -> None:
        """Test getting all videos with include_deleted parameter."""
        videos = await usecase.execute(include_deleted=True)
        assert videos is not None
        assert len(videos) == 1

        repository.get_all.assert_awaited_once_with(
            offset=0, limit=20, include_deleted=True
        )

    async def test_get_all_videos_with_user_id_and_include_deleted(
        self: Self,
        usecase: GetAllVideosUseCase,
        repository: AsyncMock,
        video: Video,
    ) -> None:
        """Test getting all videos with user_id and include_deleted parameters."""
        repository.get_all_with_favorite_mark.return_value = [video]

        videos = await usecase.execute(user_id="test_user_id", include_deleted=True)
        assert videos is not None
        assert len(videos) == 1

        repository.get_all_with_favorite_mark.assert_awaited_once_with(
            "test_user_id",
            0,
            20,
            include_deleted=True,
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

    async def test_soft_delete_video(
        self: Self,
        usecase: DeleteVideoUseCase,
        repository: AsyncMock,
        video: Video,
        full_text_repository: AsyncMock,
        permissions_repo: AsyncMock,
    ) -> None:
        repository.get_by_id.return_value = video

        await usecase.execute(video.id, DeleteType.TEMPORARY)

        repository.get_by_id.assert_awaited_once_with(video.id, include_deleted=True)
        repository.delete.assert_awaited_once_with(
            video.id,
            type_=DeleteType.TEMPORARY,
        )
        full_text_repository.delete.assert_awaited_once_with(video.id)
        permissions_repo.delete.assert_awaited_once_with(
            Object("video", video.slug), "reader"
        )

    async def test_permanent_delete_active_video(
        self: Self,
        usecase: DeleteVideoUseCase,
        repository: AsyncMock,
        video: Video,
        full_text_repository: AsyncMock,
        permissions_repo: AsyncMock,
    ) -> None:
        repository.get_by_id.return_value = video

        await usecase.execute(video.id, DeleteType.PERMANENT)

        repository.get_by_id.assert_awaited_once_with(video.id, include_deleted=True)
        repository.delete.assert_awaited_once_with(
            video.id,
            type_=DeleteType.PERMANENT,
        )
        full_text_repository.delete.assert_awaited_once_with(video.id)
        # Should remove reader permissions for permanent deletion of active video
        permissions_repo.delete.assert_awaited_once_with(
            Object("video", video.slug), "reader"
        )

    async def test_permanent_delete_soft_deleted_video(
        self: Self,
        usecase: DeleteVideoUseCase,
        repository: AsyncMock,
        video: Video,
        full_text_repository: AsyncMock,
        permissions_repo: AsyncMock,
    ) -> None:
        # Create a soft-deleted video
        video_data = video.model_dump()
        video_data.update({"deleted": True, "delete_type": DeleteType.TEMPORARY})
        soft_deleted_video = Video(**video_data)
        repository.get_by_id.return_value = soft_deleted_video

        await usecase.execute(video.id, DeleteType.PERMANENT)

        repository.get_by_id.assert_awaited_once_with(video.id, include_deleted=True)
        repository.delete.assert_awaited_once_with(
            video.id,
            type_=DeleteType.PERMANENT,
        )
        full_text_repository.delete.assert_awaited_once_with(video.id)
        # Should remove both reader and writer permissions for permanent deletion
        assert permissions_repo.delete.await_count == 2
        permissions_repo.delete.assert_any_await(Object("video", video.slug), "reader")
        permissions_repo.delete.assert_any_await(Object("video", video.slug), "writer")

    async def test_soft_delete_already_soft_deleted_video_raises_exception(
        self: Self,
        usecase: DeleteVideoUseCase,
        repository: AsyncMock,
        video: Video,
        full_text_repository: AsyncMock,
    ) -> None:
        # Create a soft-deleted video
        video_data = video.model_dump()
        video_data.update({"deleted": True, "delete_type": DeleteType.TEMPORARY})
        soft_deleted_video = Video(**video_data)
        repository.get_by_id.return_value = soft_deleted_video

        with pytest.raises(VideoAlreadyDeletedError):
            await usecase.execute(video.id, DeleteType.TEMPORARY)

        repository.get_by_id.assert_awaited_once_with(video.id, include_deleted=True)
        repository.delete.assert_not_called()
        full_text_repository.delete.assert_not_called()

    async def test_delete_video_with_invalid_id(
        self: Self,
        usecase: DeleteVideoUseCase,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
    ) -> None:
        repository.get_by_id.side_effect = VideoNotFoundError

        with pytest.raises(VideoNotFoundError):
            await usecase.execute(100_000_000)

        repository.get_by_id.assert_awaited_once_with(100_000_000, include_deleted=True)
        repository.delete.assert_not_called()
        full_text_repository.delete.assert_not_called()

    async def test_delete_video_without_permissions_repo(
        self: Self,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
        video: Video,
    ) -> None:
        usecase = DeleteVideoUseCase(repository, full_text_repository, None)
        repository.get_by_id.return_value = video

        await usecase.execute(video.id, DeleteType.TEMPORARY)

        repository.get_by_id.assert_awaited_once_with(video.id, include_deleted=True)
        repository.delete.assert_awaited_once_with(
            video.id,
            type_=DeleteType.TEMPORARY,
        )
        full_text_repository.delete.assert_awaited_once_with(video.id)


class TestRestoreVideoUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self: Self,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
    ) -> None:
        full_text_repository.create.return_value = None

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
        permissions_repo: AsyncMock,
    ) -> RestoreVideoUseCase:
        return RestoreVideoUseCase(
            repository,
            full_text_repository,
            permissions_repo,
        )

    async def test_restore_video(
        self: Self,
        usecase: RestoreVideoUseCase,
        repository: AsyncMock,
        video: Video,
        full_text_repository: AsyncMock,
        permissions_repo: AsyncMock,
    ) -> None:
        repository.restore.return_value = video

        result = await usecase.execute(video.id)

        assert result == video
        repository.restore.assert_awaited_once_with(video.id)
        full_text_repository.restore.assert_awaited_once_with(video)
        permissions_repo.write.assert_awaited_once_with(
            Object("video", video.slug),
            "reader",
            Object("user", "*"),
        )

    async def test_restore_video_not_found(
        self: Self,
        usecase: RestoreVideoUseCase,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
    ) -> None:
        repository.restore.side_effect = VideoNotFoundError

        with pytest.raises(VideoNotFoundError):
            await usecase.execute(100_000_000)

        repository.restore.assert_awaited_once_with(100_000_000)
        full_text_repository.create.assert_not_called()

    async def test_restore_video_not_deleted(
        self: Self,
        usecase: RestoreVideoUseCase,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
        video: Video,
    ) -> None:
        repository.restore.side_effect = VideoNotDeletedError

        with pytest.raises(VideoNotDeletedError):
            await usecase.execute(video.id)

        repository.restore.assert_awaited_once_with(video.id)
        full_text_repository.create.assert_not_called()

    async def test_restore_video_without_permissions_repo(
        self: Self,
        repository: AsyncMock,
        full_text_repository: AsyncMock,
        video: Video,
    ) -> None:
        usecase = RestoreVideoUseCase(repository, full_text_repository, None)
        repository.restore.return_value = video

        result = await usecase.execute(video.id)

        assert result == video
        repository.restore.assert_awaited_once_with(video.id)
        full_text_repository.restore.assert_awaited_once_with(video)
