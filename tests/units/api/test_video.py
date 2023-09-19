import pytest
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from app.internal.controller.http import app
from app.internal.controller.http.v1.dependencies.video import find_video
from app.internal.entity.video import NewVideoDto, Video
from app.internal.usecase.exceptions.video import (
    VideoYtIdNotUniqueError,
)


@pytest.fixture()
def _mock_find_video(
    video: Video,
) -> None:
    app.dependency_overrides[find_video] = lambda: video


class TestGetVideos:
    async def test_get_videos(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        video: Video,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.video.GetAllVideosUseCase.execute",
            return_value=[video],
        )
        mocked_count = mocker.patch(
            "app.internal.usecase.video.GetCountVideosUseCase.execute",
            return_value=1,
        )
        response = await client.get("/videos")

        mocked.assert_awaited_once()
        mocked_count.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["X-Total-Count"] == "1"


class TestGetVideo:
    @pytest.mark.usefixtures("_mock_find_video")
    async def test_get_video(
        self: Self,
        client: AsyncClient,
        video: Video,
    ) -> None:
        response = await client.get(f"/videos/{video.slug}")

        assert response.status_code == status.HTTP_200_OK


class TestDeleteVideo:
    @pytest.mark.usefixtures("_mock_current_user", "_mock_find_video")
    async def test_delete_video(
        self: Self,
        client: AsyncClient,
        video: Video,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.video.DeleteVideoUseCase.execute",
        )
        response = await client.delete(f"/videos/{video.slug}")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestCreateVideo:
    @pytest.fixture()
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

    @pytest.mark.usefixtures("_mock_current_user")
    async def test_create_video(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        video: Video,
        data: NewVideoDto,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.video.CreateVideoUseCase.execute",
            return_value=video,
        )
        response = await client.post(
            "/videos",
            content=data.model_dump_json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.usefixtures("_mock_current_user")
    async def test_already_exists(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        data: NewVideoDto,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.video.CreateVideoUseCase.execute",
            side_effect=VideoYtIdNotUniqueError(data.yt_id),
        )
        response = await client.post(
            "/videos",
            content=data.model_dump_json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_409_CONFLICT
