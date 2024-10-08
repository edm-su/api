import pytest
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from edm_su_api.internal.controller.http import app
from edm_su_api.internal.controller.http.v1.dependencies.video import (
    find_video,
)
from edm_su_api.internal.entity.video import Video
from edm_su_api.internal.usecase.exceptions.user_videos import (
    UserVideoAlreadyLikedError,
    UserVideoNotLikedError,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def mock_find_video(video: Video) -> None:
    app.dependency_overrides[find_video] = lambda: video


class TestLikeVideo:
    @pytest.mark.usefixtures("mock_current_user", "mock_find_video")
    async def test_like_video(
        self: Self,
        client: AsyncClient,
        video: Video,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.user_videos.LikeVideoUseCase.execute",
            return_value=None,
        )
        response = await client.post(f"/videos/{video.slug}/like")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.usefixtures("mock_current_user", "mock_find_video")
    async def test_already_liked(
        self: Self,
        client: AsyncClient,
        video: Video,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.user_videos.LikeVideoUseCase.execute",
            side_effect=UserVideoAlreadyLikedError,
        )
        response = await client.post(f"/videos/{video.slug}/like")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_409_CONFLICT


class TestUnlikeVideo:
    @pytest.mark.usefixtures("mock_current_user", "mock_find_video")
    async def test_unlike_video(
        self: Self,
        client: AsyncClient,
        video: Video,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.user_videos.UnlikeVideoUseCase.execute",
            return_value=None,
        )
        response = await client.delete(f"/videos/{video.slug}/like")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.usefixtures("mock_current_user", "mock_find_video")
    async def test_not_liked(
        self: Self,
        client: AsyncClient,
        video: Video,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.user_videos.UnlikeVideoUseCase.execute",
            side_effect=UserVideoNotLikedError,
        )
        response = await client.delete(f"/videos/{video.slug}/like")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_409_CONFLICT


class TestGetUserVideos:
    async def test_get_user_videos(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        video: Video,
        user_auth_headers: dict[str, str],
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.user_videos.GetUserVideosUseCase.execute",
            return_value=[video],
        )
        response = await client.get(
            "/user/videos",
            headers=user_auth_headers,
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
