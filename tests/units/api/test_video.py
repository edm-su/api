import pytest
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from edm_su_api.internal.controller.http import app
from edm_su_api.internal.controller.http.v1.dependencies.video import (
    find_video,
)
from edm_su_api.internal.entity.user import User
from edm_su_api.internal.entity.video import NewVideoDto, Video
from edm_su_api.internal.usecase.exceptions.video import (
    VideoNotFoundError,
    VideoYtIdNotUniqueError,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def mock_find_video(
    video: Video,
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        "edm_su_api.internal.usecase.video.GetVideoBySlugUseCase.execute",
        return_value=video,
    )
    app.dependency_overrides[find_video] = lambda: video


class TestGetVideos:
    @pytest.mark.usefixtures("mock_anonymous_user")
    async def test_get_videos(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        video: Video,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.video.GetAllVideosUseCase.execute",
            return_value=[video],
        )
        mocked_count = mocker.patch(
            "edm_su_api.internal.usecase.video.GetCountVideosUseCase.execute",
            return_value=1,
        )
        response = await client.get("/videos")

        mocked.assert_awaited_once_with(offset=0, limit=25, user_id=None)
        mocked_count.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["X-Total-Count"] == "1"

    @pytest.mark.usefixtures("mock_current_user")
    async def test_get_videos_authorized(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        video: Video,
        user: User,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.video.GetAllVideosUseCase.execute",
            return_value=[video],
        )
        mocked_count = mocker.patch(
            "edm_su_api.internal.usecase.video.GetCountVideosUseCase.execute",
            return_value=1,
        )
        response = await client.get("/videos")

        mocked.assert_awaited_once_with(offset=0, limit=25, user_id=user.id)
        mocked_count.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["X-Total-Count"] == "1"


class TestGetVideo:
    @pytest.mark.usefixtures("mock_find_video", "mock_anonymous_user")
    async def test_get_video(
        self: Self,
        client: AsyncClient,
        video: Video,
    ) -> None:
        response = await client.get(f"/videos/{video.slug}")

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.usefixtures("mock_find_video", "mock_current_user")
    async def test_get_video_authorized(
        self: Self,
        client: AsyncClient,
        video: Video,
    ) -> None:
        response = await client.get(f"/videos/{video.slug}")

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.usefixtures("mock_anonymous_user")
    async def test_get_video_not_found(
        self,
        client: AsyncClient,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.video.GetVideoBySlugUseCase.execute",
            side_effect=VideoNotFoundError,
        )
        response = await client.get("/videos/404video")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteVideo:
    @pytest.mark.usefixtures("mock_current_user", "mock_find_video")
    async def test_delete_video(
        self: Self,
        client: AsyncClient,
        video: Video,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.video.DeleteVideoUseCase.execute",
        )
        response = await client.delete(f"/videos/{video.slug}")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestCreateVideo:
    @pytest.fixture
    def data(
        self: Self,
        video: Video,
    ) -> NewVideoDto:
        return NewVideoDto(
            title=video.title,
            date=video.date,
            yt_id=video.yt_id,
            yt_thumbnail=video.yt_thumbnail,
            duration=video.duration,
            slug=video.slug,
        )

    @pytest.mark.usefixtures("mock_current_user")
    async def test_create_video(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        video: Video,
        data: NewVideoDto,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.video.CreateVideoUseCase.execute",
            return_value=video,
        )
        response = await client.post(
            "/videos",
            content=data.model_dump_json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.usefixtures("mock_current_user")
    async def test_already_exists(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        data: NewVideoDto,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.video.CreateVideoUseCase.execute",
            side_effect=VideoYtIdNotUniqueError(data.yt_id),
        )
        response = await client.post(
            "/videos",
            content=data.model_dump_json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_409_CONFLICT
