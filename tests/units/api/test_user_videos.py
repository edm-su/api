import pytest
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from app.internal.controller.http.v1.dependencies.video import find_video
from app.internal.entity.user import User
from app.internal.entity.video import Video
from app.internal.usecase.exceptions.user import UserNotFoundError
from app.internal.usecase.exceptions.user_videos import (
    UserVideoAlreadyLikedError,
    UserVideoNotLikedError,
)
from app.main import app


@pytest.fixture()
def _mock_find_video(video: Video) -> None:
    app.dependency_overrides[find_video] = lambda: video


class TestLikeVideo:
    @pytest.mark.usefixtures("_mock_current_user", "_mock_find_video")
    async def test_like_video(
        self: Self,
        client: AsyncClient,
        video: Video,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user_videos.LikeVideoUseCase.execute",
            return_value=None,
        )
        response = await client.post(f"/videos/{video.slug}/like")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.usefixtures("_mock_current_user", "_mock_find_video")
    async def test_already_liked(
        self: Self,
        client: AsyncClient,
        video: Video,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user_videos.LikeVideoUseCase.execute",
            side_effect=UserVideoAlreadyLikedError,
        )
        response = await client.post(f"/videos/{video.slug}/like")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.usefixtures("_mock_find_video")
    async def test_without_permission(
        self: Self,
        client: AsyncClient,
        video: Video,
    ) -> None:
        response = await client.post(f"/videos/{video.slug}/like")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUnlikeVideo:
    @pytest.mark.usefixtures("_mock_current_user", "_mock_find_video")
    async def test_unlike_video(
        self: Self,
        client: AsyncClient,
        video: Video,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user_videos.UnlikeVideoUseCase.execute",
            return_value=None,
        )
        response = await client.delete(f"/videos/{video.slug}/like")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.usefixtures("_mock_current_user", "_mock_find_video")
    async def test_not_liked(
        self: Self,
        client: AsyncClient,
        video: Video,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user_videos.UnlikeVideoUseCase.execute",
            side_effect=UserVideoNotLikedError,
        )
        response = await client.delete(f"/videos/{video.slug}/like")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.usefixtures("_mock_find_video")
    async def test_without_permission(
        self: Self,
        client: AsyncClient,
        video: Video,
    ) -> None:
        response = await client.delete(f"/videos/{video.slug}/like")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetUserVideos:
    async def test_get_user_videos(
        self: Self,
        client: AsyncClient,
        user: User,
        mocker: MockerFixture,
        video: Video,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user_videos.GetUserVideosUseCase.execute",
            return_value=[video],
        )
        mocked_user = mocker.patch(
            "app.internal.usecase.user.GetUserByUsernameUseCase.execute",
            return_value=user,
        )
        response = await client.get(f"/users/{user.username}/videos")

        mocked.assert_awaited_once()
        mocked_user.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    async def test_user_not_found(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        user: User,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.GetUserByUsernameUseCase.execute",
            side_effect=UserNotFoundError,
        )
        response = await client.get(f"/users/{user.username}/videos")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_404_NOT_FOUND
