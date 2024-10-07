from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pytest_mock import MockFixture
from typing_extensions import Self

from edm_su_api.internal.entity.user import User
from edm_su_api.internal.entity.video import Video
from edm_su_api.internal.usecase.exceptions.user_videos import (
    UserVideoAlreadyLikedError,
    UserVideoNotLikedError,
)
from edm_su_api.internal.usecase.repository.user_videos import (
    AbstractUserVideosRepository,
)
from edm_su_api.internal.usecase.user_videos import (
    GetUserVideosUseCase,
    LikeVideoUseCase,
    UnlikeVideoUseCase,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def repository(mocker: MockFixture) -> AsyncMock:
    return mocker.AsyncMock(spec=AbstractUserVideosRepository)


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


class TestGetUserVideosUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self: Self,
        repository: AsyncMock,
        video: Video,
    ) -> None:
        repository.get_user_videos.return_value = [video]

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetUserVideosUseCase:
        return GetUserVideosUseCase(repository)

    async def test_get_user_videos(
        self: Self,
        usecase: GetUserVideosUseCase,
        user: User,
        video: Video,
        repository: AsyncMock,
    ) -> None:
        result = await usecase.execute(user, limit=1, skip=1)

        assert result == [video]
        repository.get_user_videos.assert_awaited_once_with(
            user,
            limit=1,
            offset=1,
        )


class TestLikeVideoUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        repository.is_liked.return_value = False
        repository.like_video.return_value = None

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> LikeVideoUseCase:
        return LikeVideoUseCase(repository)

    async def test_like_video(
        self: Self,
        usecase: LikeVideoUseCase,
        user: User,
        video: Video,
        repository: AsyncMock,
    ) -> None:
        await usecase.execute(user, video)

        repository.is_liked.assert_awaited_once_with(user, video)
        repository.like_video.assert_awaited_once_with(user, video)

    async def test_like_video_already_liked(
        self: Self,
        usecase: LikeVideoUseCase,
        user: User,
        video: Video,
        repository: AsyncMock,
    ) -> None:
        repository.is_liked.return_value = True

        with pytest.raises(UserVideoAlreadyLikedError):
            await usecase.execute(user, video)

        repository.is_liked.assert_awaited_once_with(user, video)
        repository.like_video.assert_not_awaited()


class TestUnlikeVideoUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        repository.is_liked.return_value = True
        repository.unlike_video.return_value = None

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> UnlikeVideoUseCase:
        return UnlikeVideoUseCase(repository)

    async def test_unlike_video(
        self: Self,
        usecase: UnlikeVideoUseCase,
        user: User,
        video: Video,
        repository: AsyncMock,
    ) -> None:
        await usecase.execute(user, video)

        repository.is_liked.assert_awaited_once_with(user, video)
        repository.unlike_video.assert_awaited_once_with(user, video)

    async def test_unlike_video_not_liked(
        self: Self,
        usecase: UnlikeVideoUseCase,
        user: User,
        video: Video,
        repository: AsyncMock,
    ) -> None:
        repository.is_liked.return_value = False

        with pytest.raises(UserVideoNotLikedError):
            await usecase.execute(user, video)

        repository.is_liked.assert_awaited_once_with(user, video)
        repository.unlike_video.assert_not_awaited()
